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
import logging
from xml.etree.ElementTree import Element

from utils.base_elements import BaseElementParser
from utils.helper import check_valid_id
from .conformance_parser import is_restricted_by_conformance

logger = logging.getLogger(__name__)


class ClusterElementBaseParser(BaseElementParser):
    """Base for cluster element parsers (attribute, command, event). Shared skip and id/name logic."""

    def __init__(self, cluster, feature_map, allowed_ids, base_elements=None):
        self.cluster = cluster
        self.feature_map = feature_map or {}
        self.allowed_ids = allowed_ids or []
        self.base_elements = base_elements or []
        self.processed = set()

    def can_skip(self, elem: Element) -> (bool, str):
        """Return True if this element should be skipped (invalid, filtered, or conformance)."""
        name = elem.get("name")
        if not name:
            return True, "missing name"
        if name in self.processed:
            return True, "already processed"
        self.processed.add(name)

        base_list = self.base_elements
        base = next((b for b in base_list if getattr(b, "name", None) == name), None)
        if base:
            self._fill_from_base(elem, base)

        elem_id = elem.get("id")
        if not check_valid_id(elem_id):
            return True, "invalid id"
        if not (name and elem_id):
            return True, "missing name or id"
        if self.allowed_ids and int(elem_id, 16) not in self.allowed_ids:
            return True, "id not in allowed list"
        if is_restricted_by_conformance(self.feature_map, elem):
            return True, "conformance restrictions"
        return False, "Unknown reason"

    def _fill_from_base(self, elem: Element, base):
        """Fill elem from base when attribute is missing. Override in AttributeParser to also set type."""
        if not elem.get("id", None) and getattr(base, "id", None):
            elem.set("id", base.id)
