Data Model
==========

This has the high level APIs for Data Model.

Generated Data Model
====================

When **Enable Generated Data Model** is enabled in ``menuconfig``
(``CONFIG_ESP_MATTER_ENABLE_GENERATED_DATA_MODEL``), ESP-Matter uses the
auto-generated data model instead of the legacy (manually implemented) one.

Source Selection
----------------

- Generated implementation is used from::

      components/esp_matter/data_model/generated/

- Legacy implementation (used when disabled) is located at::

      components/esp_matter/data_model/legacy/

Directory Structure
-------------------

- **Clusters**

  ::

      generated/clusters/<cluster>/

  Example (On/Off cluster):

  ::

      on_off/on_off.h
      on_off/on_off.cpp
      on_off/on_off_ids.h

- **Device Types**

  ::

      generated/device_types/<device>_device/

  Example (Extended Color Light):

  ::

      extended_color_light_device/extended_color_light_device.h
      extended_color_light_device/extended_color_light_device.cpp

Regenerating the Data Model
---------------------------

To regenerate the data model files, run the following command from the
ESP-Matter repository root::

    python tools/data_model_gen/data_model_gen.py

For more details, refer to::

    tools/data_model_gen/README.md

Summary
-------

- Enable ``CONFIG_ESP_MATTER_ENABLE_GENERATED_DATA_MODEL`` to use generated clusters and device types.
- Disable it to use the legacy implementation.
- The generated model improves maintainability and alignment with the data model definition as per the Matter specification.

API reference
-------------

.. include-build-file:: inc/esp_matter_data_model.inc
