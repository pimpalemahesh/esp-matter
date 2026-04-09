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

"""Tests for xml_processing/serializers.py — dict conversion for all element types."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from xml_processing.elements import Attribute, Command, Event, Feature, Cluster, Device
from xml_processing.data_type_parser import Item, Enum, Bitmap, Struct
from xml_processing.serializers import DataTypeSerializer


class TestAttributeSerialization(unittest.TestCase):
    """Test Attribute.to_dict() serialization."""

    def test_basic_attribute_dict(self):
        attr = Attribute(name="TestAttr", id="0x0000", type_="bool", default_value="false", is_mandatory=True)
        d = attr.to_dict()
        self.assertIn("name", d)
        self.assertEqual(d["id"], "0x0000")
        self.assertEqual(d["type"], "bool")
        self.assertIn("default_value", d)
        self.assertIn("flags", d)
        self.assertIn("mandatory", d)

    def test_attribute_with_bounds(self):
        attr = Attribute(name="temp", id="0x0001", type_="int16", default_value="0", is_mandatory=True)
        attr.min_value = -100
        attr.max_value = 100
        d = attr.to_dict()
        self.assertEqual(d["min_value"], -100)
        self.assertEqual(d["max_value"], 100)

    def test_attribute_with_access(self):
        access = Attribute.Access(read="true", readPrivilege="view", write="true", writePrivilege="operate")
        attr = Attribute(name="test", id="0x0001", type_="uint8", default_value="0",
                         is_mandatory=True, access=access)
        d = attr.to_dict()
        self.assertIsNotNone(d["access"])

    def test_attribute_nullable(self):
        quality = Attribute.Quality(changeOmitted="false", nullable="true", scene="false",
                                     persistence="volatile", reportable="false")
        attr = Attribute(name="test", id="0x0001", type_="uint8", default_value="0",
                         is_mandatory=True, quality=quality)
        d = attr.to_dict()
        self.assertTrue(d["nullable"])


class TestCommandSerialization(unittest.TestCase):
    """Test Command.to_dict() serialization."""

    def test_basic_command_dict(self):
        cmd = Command(id="0x0001", name="Off", direction="commandToServer", response="Y", is_mandatory=True)
        d = cmd.to_dict()
        self.assertEqual(d["name"], "Off")
        self.assertEqual(d["id"], "0x0001")
        self.assertIn("direction", d)
        self.assertIn("flags", d)

    def test_command_with_fields(self):
        cmd = Command(id="0x0001", name="MoveToLevel", direction="commandToServer",
                      response="Y", is_mandatory=True)
        field = Command.CommandField(id="0x00", name="level", type_="uint8")
        cmd.add_field(field)
        d = cmd.to_dict()
        self.assertIn("fields", d)
        self.assertEqual(len(d["fields"]), 1)


class TestEventSerialization(unittest.TestCase):
    """Test Event.to_dict() serialization."""

    def test_basic_event_dict(self):
        evt = Event(id="0x0001", name="StateChange", is_mandatory=True)
        d = evt.to_dict()
        self.assertEqual(d["name"], "StateChange")
        self.assertEqual(d["id"], "0x0001")
        self.assertIn("mandatory", d)


class TestFeatureSerialization(unittest.TestCase):
    """Test Feature.to_dict() serialization."""

    def test_basic_feature_dict(self):
        feat = Feature(name="Lighting", code="LT", id="0x0001")
        d = feat.to_dict()
        self.assertEqual(d["name"], feat.name)
        self.assertEqual(d["id"], "0x0001")
        self.assertIn("code", d)
        self.assertEqual(d["code"], "LT")

    def test_feature_with_attributes(self):
        feat = Feature(name="Lighting", code="LT", id="0x0001")
        attr = Attribute(name="Level", id="0x0002", type_="uint8", default_value="0", is_mandatory=True)
        feat.add_attribute_list({attr})
        d = feat.to_dict()
        self.assertIn("attributes", d)
        self.assertEqual(len(d["attributes"]), 1)


class TestClusterSerialization(unittest.TestCase):
    """Test Cluster.to_dict() serialization."""

    def test_basic_cluster_dict(self):
        c = Cluster(name="OnOff", id="0x0006", revision=6)
        d = c.to_dict()
        self.assertEqual(d["name"], c.name)
        self.assertEqual(d["id"], "0x0006")
        self.assertEqual(d["revision"], 6)
        self.assertIn("attributes", d)
        self.assertIn("commands", d)
        self.assertIn("events", d)
        self.assertIn("features", d)

    def test_cluster_with_elements(self):
        c = Cluster(name="OnOff", id="0x0006", revision=6)
        attr = Attribute(name="OnOff", id="0x0000", type_="bool", default_value="false", is_mandatory=True)
        cmd = Command(id="0x0001", name="Off", direction="commandToServer", response="Y", is_mandatory=True)
        c.attributes.add(attr)
        c.commands.add(cmd)
        d = c.to_dict()
        self.assertEqual(len(d["attributes"]), 1)
        self.assertEqual(len(d["commands"]), 1)


class TestDeviceSerialization(unittest.TestCase):
    """Test Device.to_dict() serialization."""

    def test_basic_device_dict(self):
        dev = Device(id="0x0100", name="On/Off Light", revision=3)
        d = dev.to_dict()
        self.assertIn("name", d)
        self.assertEqual(d["id"], "0x0100")
        self.assertIn("clusters", d)

    def test_device_with_clusters(self):
        dev = Device(id="0x0100", name="On/Off Light", revision=3)
        c = Cluster(name="OnOff", id="0x0006", revision=6)
        c.server_cluster = True
        dev.clusters.add(c)
        d = dev.to_dict()
        self.assertEqual(len(d["clusters"]), 1)


class TestDataTypeSerializer(unittest.TestCase):
    """Test DataTypeSerializer — data type dict conversion."""

    def test_serialize_enums(self):
        items = [Item("A", "0", "", True), Item("B", "1", "", False)]
        enums = {"TestEnum": Enum("TestEnum", "enum8", items)}
        result = DataTypeSerializer.to_dict({"enums": enums})
        self.assertIn("enums", result)
        self.assertEqual(len(result["enums"]), 1)

    def test_serialize_empty(self):
        result = DataTypeSerializer.to_dict({"enums": {}, "bitmaps": {}})
        self.assertEqual(len(result["enums"]), 0)


if __name__ == "__main__":
    unittest.main()
