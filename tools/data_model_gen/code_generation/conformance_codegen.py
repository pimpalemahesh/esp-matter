# Copyright 2026 Espressif Systems (Shanghai) PTE LTD
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
from utils.conformance import (
    ConformanceDecision,
    get_conformance_type,
    ConformanceTAG,
    BaseConformance,
    Choice,
)
from utils.exceptions import CodeGenerationError

logger = logging.getLogger(__name__)

# Conformance type constants
MANDATORY_CONFORM = "mandatory"
OPTIONAL_CONFORM = "optional"
OTHERWISE_CONFORM = "otherwise"
DEPRECATE_CONFORM = "deprecate"
DISALLOWED_CONFORM = "disallowed"
PROVISIONAL_CONFORM = "provisional"

KEY_TYPE = "type"


class ExprIterator(ABC):
    @abstractmethod
    def iterate_attribute(self, expr): ...

    @abstractmethod
    def iterate_feature(self, expr): ...

    @abstractmethod
    def iterate_command(self, expr): ...

    @abstractmethod
    def iterate_true(self, expr): ...

    @abstractmethod
    def iterate_false(self, expr): ...

    @abstractmethod
    def iterate_non(self, expr): ...

    @abstractmethod
    def iterate_not(self, expr): ...

    @abstractmethod
    def iterate_and(self, expr): ...

    @abstractmethod
    def iterate_or(self, expr): ...

    @abstractmethod
    def iterate_wrapper(self, expr): ...

    @abstractmethod
    def iterate_otherwise(self, expr): ...


def filter_operand(operands: List[Expr]) -> List[Expr]:
    """Filter out the operands that are not valid expressions."""
    return [
        op
        for op in operands
        if op() is not None and "true" not in op() and "false" not in op()
    ]


class Expr(ABC):
    @abstractmethod
    def __call__(self) -> str: ...

    @abstractmethod
    def iterate(self, iterator: ExprIterator): ...


class NonExpr(Expr):
    def __call__(self) -> str:
        return None

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_non(self)


class TrueExpr(Expr):
    def __call__(self) -> str:
        return "true"

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_true(self)


class FalseExpr(Expr):
    def __call__(self) -> str:
        return "false"

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_false(self)


class AttributeExpr(Expr):
    def __init__(self, attr_name: str):
        self.attr_name = attr_name

    def __call__(self) -> str:
        return f"esp_matter::attribute::get(cluster, attribute::{self.attr_name}::Id) != nullptr"

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_attribute(self)


class CommandExpr(Expr):
    def __init__(self, command_name: str, flag: str):
        self.command_name = command_name
        self.flag = flag

    def __call__(self) -> str:
        return f"esp_matter::command::get(cluster, command::{self.command_name}::Id, {self.flag}) != nullptr"

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_command(self)


class FeatureExpr(Expr):
    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    def __call__(self) -> str:
        return f"feature_map & feature::{self.feature_name}::get_id()"

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_feature(self)


class AndExpr(Expr):
    def __init__(self, operands: List[Expr]):
        self.operands = filter_operand(operands)

    def __call__(self) -> str:
        joined_expr = " && ".join(f"({op()})" for op in self.operands)
        return f"({joined_expr})" if len(self.operands) > 0 else None

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_and(self)
        for op in self.operands:
            op.iterate(iterator)


class OrExpr(Expr):
    def __init__(self, operands: List[Expr]):
        self.operands = filter_operand(operands)

    def __call__(self) -> str:
        joined_expr = " || ".join(f"({op()})" for op in self.operands)
        return f"({joined_expr})" if len(self.operands) > 0 else None

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_or(self)
        for op in self.operands:
            op.iterate(iterator)


class NotExpr(Expr):
    def __init__(self, operand: Expr):
        self.operand = operand

    def __call__(self) -> str:
        return f"!({self.operand()})"

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_not(self)
        self.operand.iterate(iterator)


class WrapperExpr(Expr):
    def __init__(self, operand: Expr):
        self.operand = operand

    def __call__(self) -> str:
        return self.operand()

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_wrapper(self)
        self.operand.iterate(iterator)


class MandatoryExpr(WrapperExpr):
    pass


class OptionalExpr(WrapperExpr):
    pass


class DeprecateExpr(WrapperExpr):
    def __call__(self) -> str:
        return f"(!({self.operand()}))"


class DisallowedExpr(WrapperExpr):
    def __call__(self) -> str:
        return f"(!({self.operand()}))"


class OtherwiseExpr(Expr):
    def __init__(self, operands: List[Expr]):
        self.operands = filter_operand(operands)

    def __call__(self) -> str:
        joined_expr = " || ".join(op() for op in self.operands)
        return f"({joined_expr})" if len(self.operands) > 0 else None

    def iterate(self, iterator: ExprIterator):
        iterator.iterate_otherwise(self)
        for op in self.operands:
            op.iterate(iterator)


def parse_expr(obj: dict) -> Expr:
    """Parse the conformance dictionary and return the corresponding Expr object.
    :param obj: The conformance expression in dictionary format.
    :returns: The corresponding Expr object.
    """
    if obj is None:
        return NonExpr()

    elif isinstance(obj, bool):
        return TrueExpr() if obj else FalseExpr()

    elif ConformanceTAG.ATTRIBUTE.value in obj:
        return AttributeExpr(obj[ConformanceTAG.ATTRIBUTE.value])

    elif ConformanceTAG.FEATURE.value in obj:
        return FeatureExpr(obj[ConformanceTAG.FEATURE.value])

    elif ConformanceTAG.COMMAND.value in obj:
        if ConformanceTAG.COMMAND_FLAG.value not in obj:
            raise CodeGenerationError(
                f"Command flag not found for command: {obj[ConformanceTAG.COMMAND.value]}",
                context="conformance_codegen.parse_expr",
                suggestion="Ensure the conformance JSON includes commandFlag for the command.",
            )
        return CommandExpr(
            obj[ConformanceTAG.COMMAND.value], obj[ConformanceTAG.COMMAND_FLAG.value]
        )

    elif ConformanceTAG.NOT.value in obj:
        return NotExpr(parse_expr(obj[ConformanceTAG.NOT.value]))

    elif ConformanceTAG.AND.value in obj:
        return AndExpr([parse_expr(x) for x in obj[ConformanceTAG.AND.value]])

    elif ConformanceTAG.OR.value in obj:
        return OrExpr([parse_expr(x) for x in obj[ConformanceTAG.OR.value]])

    elif ConformanceTAG.GREATER.value in obj:
        logger.debug(f"Greater than condition not supported: {obj}")
        return NonExpr()

    else:
        logger.debug(f"Unknown conformance expression: {obj}")
        return NonExpr()


def parse_choice(conformance: Dict[str, Any]) -> Optional[Choice]:
    if not conformance:
        return None
    choice = conformance.get("choice")
    if choice:
        more = bool(conformance.get("more", False))
        return Choice(choice, more)

    nested_conformance = conformance.get(ConformanceTAG.CONDITION.value, {})
    nested_optional_conformance = nested_conformance.get(OPTIONAL_CONFORM, {})
    if nested_optional_conformance:
        if isinstance(nested_optional_conformance, list):
            for cond in nested_optional_conformance:
                choice = cond.get("choice")
                more = bool(cond.get("more", False))
                return Choice(choice, more)
        elif isinstance(nested_optional_conformance, dict):
            choice = nested_optional_conformance.get("choice")
            more = bool(nested_optional_conformance.get("more", False))
            return Choice(choice, more)
        return None
    return None


class NotIterator(ExprIterator):
    def __init__(self):
        self.found = False

    def iterate_attribute(self, expr):
        return

    def iterate_feature(self, expr):
        return

    def iterate_command(self, expr):
        return

    def iterate_true(self, expr):
        return

    def iterate_false(self, expr):
        return

    def iterate_non(self, expr):
        return

    def iterate_not(self, expr: NotExpr):
        self.found = True
        expr.operand.iterate(self)

    def iterate_and(self, expr: AndExpr):
        for op in expr.operands:
            op.iterate(self)

    def iterate_or(self, expr: OrExpr):
        for op in expr.operands:
            op.iterate(self)

    def iterate_wrapper(self, expr: WrapperExpr):
        expr.operand.iterate(self)

    def iterate_otherwise(self, expr: OtherwiseExpr):
        for op in expr.operands:
            op.iterate(self)


class Conformance(BaseConformance, Expr):
    """Conformance class."""

    condition: Expr = None
    is_not_term_present: bool = False

    def __init__(self, conformance: Dict[str, Any] = None):
        if not conformance:
            self.type = ConformanceDecision.NOT_APPLICABLE
            return
        self.conformance = conformance
        self.type = get_conformance_type(conformance.get(KEY_TYPE))
        self.choice = parse_choice(conformance)
        self.condition = self._generate_condition(conformance)
        if self.condition:
            not_iterator = NotIterator()
            self.condition.iterate(not_iterator)
            self.is_not_term_present = not_iterator.found

    def __call__(self) -> str:
        return self.condition() if self.condition else None

    def get_mandatory_condition(self) -> Expr:
        """Get the conformance condition for mandatory conformance."""
        return (
            self.condition()
            if self.type == ConformanceDecision.MANDATORY and self.condition
            else None
        )

    def get_optional_condition(self) -> Expr:
        """Get the conformance condition for optional conformance."""
        if self.type == ConformanceDecision.OPTIONAL:
            condition = self.conformance.get(ConformanceTAG.CONDITION.value, {})
            if not condition:
                return None
            return OptionalExpr(parse_expr(condition))()
        elif self.type == ConformanceDecision.OTHERWISE:
            optional_condition = self.conformance.get(
                ConformanceTAG.CONDITION.value, {}
            ).get(OPTIONAL_CONFORM)
            operands = []
            if optional_condition:
                if isinstance(optional_condition, list):
                    for cond in optional_condition:
                        operands.append(parse_expr(cond))
                else:
                    operands.append(parse_expr(optional_condition))
            return OtherwiseExpr(operands)()
        return None

    def _generate_condition(self, conformance: Dict[str, Any]) -> Expr:
        """Generate the conformance expression for the conformance.
        :param conformance: The conformance dictionary.
        :returns: The conformance expression.
        :raises: CodeGenerationError if the conformance type is invalid.
        """
        if not conformance:
            return None
        condition = conformance.get(ConformanceTAG.CONDITION.value)
        if not condition:
            return None
        if self.type == ConformanceDecision.OTHERWISE:
            operands = []
            optional_condition = condition.get(OPTIONAL_CONFORM)
            if optional_condition:
                if isinstance(optional_condition, list):
                    for cond in optional_condition:
                        operands.append(parse_expr(cond))
                else:
                    operands.append(parse_expr(optional_condition))
            mandatory_condition = condition.get(MANDATORY_CONFORM)
            if mandatory_condition:
                mandatory = parse_expr(mandatory_condition)
                operands.append(mandatory)
            deprecate_condition = condition.get(DEPRECATE_CONFORM)
            if deprecate_condition:
                deprecate = DeprecateExpr(parse_expr(deprecate_condition))
                operands.append(deprecate)
            disallowed_condition = condition.get(DISALLOWED_CONFORM)
            if disallowed_condition:
                disallowed = DisallowedExpr(parse_expr(disallowed_condition))
                operands.append(disallowed)
            return OtherwiseExpr(operands)
        elif self.type == ConformanceDecision.MANDATORY:
            return MandatoryExpr(parse_expr(condition))
        elif self.type == ConformanceDecision.OPTIONAL:
            return OptionalExpr(parse_expr(condition))
        elif self.type == ConformanceDecision.DISALLOWED:
            return DisallowedExpr(parse_expr(condition))
        elif self.type == ConformanceDecision.DEPRECATED:
            return DeprecateExpr(parse_expr(condition))
        else:
            raise CodeGenerationError(
                f"Unknown conformance type: {self.type}",
                context="conformance_codegen._generate_condition",
                suggestion="Use a valid ConformanceDecision value.",
            )

    def iterate(self, iterator: ExprIterator):
        if self.condition:
            self.condition.iterate(iterator)


class FeatureConformance(Conformance):
    """Feature Specific Conformance class."""

    # dependency on parent feature
    mandatory_parent: Optional[str] = None
    optional_parent: Optional[str] = None

    def __init__(self, conformance: Dict[str, Any] = None):
        super().__init__(conformance)
        if conformance and self.type == ConformanceDecision.OTHERWISE:
            condition = conformance.get(ConformanceTAG.CONDITION.value)
            if condition and isinstance(condition, dict):
                mandatory = condition.get(MANDATORY_CONFORM)
                if (
                    mandatory
                    and isinstance(mandatory, dict)
                    and ConformanceTAG.FEATURE.value in mandatory
                ):
                    self.mandatory_parent = mandatory[ConformanceTAG.FEATURE.value]
        elif conformance and self.type == ConformanceDecision.OPTIONAL:
            condition = conformance.get(ConformanceTAG.CONDITION.value)
            if condition and isinstance(condition, dict):
                self.optional_parent = condition.get(ConformanceTAG.FEATURE.value)

        elif conformance and self.type == ConformanceDecision.MANDATORY:
            condition = conformance.get(ConformanceTAG.CONDITION.value)
            if condition and isinstance(condition, dict):
                self.mandatory_parent = condition.get(ConformanceTAG.FEATURE.value)

    def is_exact_one(self) -> bool:
        """Check if the conformance is O.a"""
        if self.choice is None:
            return False
        return self.choice.marker is not None and not self.choice.more

    def is_at_least_one(self) -> bool:
        """Check if the conformance is O.a+"""
        if self.choice is None:
            return False
        return self.choice.marker is not None and self.choice.more
