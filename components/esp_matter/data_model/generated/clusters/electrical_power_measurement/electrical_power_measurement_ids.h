// Copyright 2026 Espressif Systems (Shanghai) PTE LTD
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/* THIS IS A GENERATED FILE, DO NOT EDIT */

#pragma once
#include <esp_matter_data_model.h>

namespace esp_matter {
namespace cluster {
namespace electrical_power_measurement {

inline constexpr uint32_t Id = 0x0090;

namespace feature {
namespace DirectCurrent {
inline constexpr uint32_t Id = 0x1;
} /* DirectCurrent */
namespace AlternatingCurrent {
inline constexpr uint32_t Id = 0x2;
} /* AlternatingCurrent */
namespace PolyphasePower {
inline constexpr uint32_t Id = 0x4;
} /* PolyphasePower */
namespace Harmonics {
inline constexpr uint32_t Id = 0x8;
} /* Harmonics */
namespace PowerQuality {
inline constexpr uint32_t Id = 0x10;
} /* PowerQuality */
} /* feature */

namespace attribute {
namespace PowerMode {
inline constexpr uint32_t Id = 0x0000;
} /* PowerMode */
namespace NumberOfMeasurementTypes {
inline constexpr uint32_t Id = 0x0001;
} /* NumberOfMeasurementTypes */
namespace Accuracy {
inline constexpr uint32_t Id = 0x0002;
} /* Accuracy */
namespace Ranges {
inline constexpr uint32_t Id = 0x0003;
} /* Ranges */
namespace Voltage {
inline constexpr uint32_t Id = 0x0004;
} /* Voltage */
namespace ActiveCurrent {
inline constexpr uint32_t Id = 0x0005;
} /* ActiveCurrent */
namespace ReactiveCurrent {
inline constexpr uint32_t Id = 0x0006;
} /* ReactiveCurrent */
namespace ApparentCurrent {
inline constexpr uint32_t Id = 0x0007;
} /* ApparentCurrent */
namespace ActivePower {
inline constexpr uint32_t Id = 0x0008;
} /* ActivePower */
namespace ReactivePower {
inline constexpr uint32_t Id = 0x0009;
} /* ReactivePower */
namespace ApparentPower {
inline constexpr uint32_t Id = 0x000A;
} /* ApparentPower */
namespace RMSVoltage {
inline constexpr uint32_t Id = 0x000B;
} /* RMSVoltage */
namespace RMSCurrent {
inline constexpr uint32_t Id = 0x000C;
} /* RMSCurrent */
namespace RMSPower {
inline constexpr uint32_t Id = 0x000D;
} /* RMSPower */
namespace Frequency {
inline constexpr uint32_t Id = 0x000E;
} /* Frequency */
namespace HarmonicCurrents {
inline constexpr uint32_t Id = 0x000F;
} /* HarmonicCurrents */
namespace HarmonicPhases {
inline constexpr uint32_t Id = 0x0010;
} /* HarmonicPhases */
namespace PowerFactor {
inline constexpr uint32_t Id = 0x0011;
} /* PowerFactor */
namespace NeutralCurrent {
inline constexpr uint32_t Id = 0x0012;
} /* NeutralCurrent */
} /* attribute */

namespace event {
namespace MeasurementPeriodRanges {
inline constexpr uint32_t Id = 0x00;
} /* MeasurementPeriodRanges */
} /* event */

} /* electrical_power_measurement */
} /* cluster */
} /* esp_matter */
