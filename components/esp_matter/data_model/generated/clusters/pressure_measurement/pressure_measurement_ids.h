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
namespace pressure_measurement {

inline constexpr uint32_t Id = 0x0403;

namespace feature {
namespace Extended {
inline constexpr uint32_t Id = 0x1;
} /* Extended */
} /* feature */

namespace attribute {
namespace MeasuredValue {
inline constexpr uint32_t Id = 0x0000;
} /* MeasuredValue */
namespace MinMeasuredValue {
inline constexpr uint32_t Id = 0x0001;
} /* MinMeasuredValue */
namespace MaxMeasuredValue {
inline constexpr uint32_t Id = 0x0002;
} /* MaxMeasuredValue */
namespace Tolerance {
inline constexpr uint32_t Id = 0x0003;
} /* Tolerance */
namespace ScaledValue {
inline constexpr uint32_t Id = 0x0010;
} /* ScaledValue */
namespace MinScaledValue {
inline constexpr uint32_t Id = 0x0011;
} /* MinScaledValue */
namespace MaxScaledValue {
inline constexpr uint32_t Id = 0x0012;
} /* MaxScaledValue */
namespace ScaledTolerance {
inline constexpr uint32_t Id = 0x0013;
} /* ScaledTolerance */
namespace Scale {
inline constexpr uint32_t Id = 0x0014;
} /* Scale */
} /* attribute */

} /* pressure_measurement */
} /* cluster */
} /* esp_matter */
