# Copyright 2025 Espressif Systems (Shanghai) PTE LTD
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
from .conformance_parser import (
    check_conformance_restrictions,
    parse_conformance,
)
from .elements import Event
from utils.helper import check_valid_id, safe_get_attr

logger = logging.getLogger(__name__)


class EventParser:

    def __init__(self, cluster, feature_map, allowed_events_ids: list = []):
        self.cluster = cluster
        self.feature_map = feature_map if feature_map else {}
        self.processed_events = set()
        self.allowed_events_ids = allowed_events_ids if allowed_events_ids else []

    def parse(self, root, base_events: list[Event] = None):
        """Iterate over all events in the cluster and create Event objects.

        :param root: The root element of the cluster XML file.
        :param base_events: The base events.
        :param base_events: list[Event]:  (Default value = None)

        """
        for event in root.findall("events/event"):
            if not self._should_process_event(event, base_events):
                continue
            logger.debug(f"Processing event {event.get('name')} for cluster {safe_get_attr(self.cluster, 'name')}")
            evt = self._create_event(event)
            evt.conformance = parse_conformance(event, self.feature_map)
            self.cluster.events.add(evt)

        # Add base events to the cluster if they are not already in the cluster
        if base_events:
            for base_event in base_events:
                if base_event.name not in self.processed_events:
                    self.cluster.events.add(base_event)

        logger.debug(
            f"Processed {len(self.cluster.events)} events for cluster {safe_get_attr(self.cluster, 'name')}"
        )

    def _should_process_event(self, event, base_events: list[Event] = None):
        """Check if event should be processed

        :param event: The event element from the cluster XML file.
        :param base_events: list[Event]:  (Default value = None)
        :returns: True if the event should be processed, False otherwise.

        """
        event_name = event.get("name")
        if not event_name:
            logger.debug(f"Skipping - missing event name {event}")
            return False
        if event_name in self.processed_events:
            return False
        self.processed_events.add(event_name)
        if base_events:
            base_event = next(
                (evt for evt in base_events if evt.name == event_name), None
            )
            if not event.get("id") and base_event:
                event.set("id", base_event.id)

        event_id = event.get("id")
        if not check_valid_id(event_id):
            return False

        if not (event_name and event_id):
            logger.warning(
                f"Skipping event due to missing required attributes event_name: {event_name} event_id: {event_id}"
            )
            return False

        if self.allowed_events_ids and int(event_id, 16) not in self.allowed_events_ids:
            logger.warning(
                f"Skipping event {event_name} id {int(event_id, 16)} due to not in allowed events"
            )
            return False

        if event_name in [safe_get_attr(e, "name") for e in self.processed_events]:
            logger.debug(f"Skipping event {event_name} due to already processed events")
            return False

        if check_conformance_restrictions(self.feature_map, event):
            logger.debug(
                f"Skipping event {event.get('name', 'unknown')} due to conformance restrictions"
            )
            return False

        return True

    def _create_event(self, event):
        """Create an Event object

        :param event:
        :returns: The created Event object.

        """
        event_name = event.get("name")
        return Event(
            id=event.get("id"),
            name=event_name,
            is_mandatory=event.find("mandatoryConform") is not None,
        )
