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
namespace time_synchronization {

inline constexpr uint32_t Id = 0x0038;

namespace feature {
namespace TimeZone {
inline constexpr uint32_t Id = 0x1;
} /* TimeZone */
namespace NTPClient {
inline constexpr uint32_t Id = 0x2;
} /* NTPClient */
namespace NTPServer {
inline constexpr uint32_t Id = 0x4;
} /* NTPServer */
namespace TimeSyncClient {
inline constexpr uint32_t Id = 0x8;
} /* TimeSyncClient */
} /* feature */

namespace attribute {
namespace UTCTime {
inline constexpr uint32_t Id = 0x0000;
} /* UTCTime */
namespace Granularity {
inline constexpr uint32_t Id = 0x0001;
} /* Granularity */
namespace TimeSource {
inline constexpr uint32_t Id = 0x0002;
} /* TimeSource */
namespace TrustedTimeSource {
inline constexpr uint32_t Id = 0x0003;
} /* TrustedTimeSource */
namespace DefaultNTP {
inline constexpr uint32_t Id = 0x0004;
} /* DefaultNTP */
namespace TimeZone {
inline constexpr uint32_t Id = 0x0005;
} /* TimeZone */
namespace DSTOffset {
inline constexpr uint32_t Id = 0x0006;
} /* DSTOffset */
namespace LocalTime {
inline constexpr uint32_t Id = 0x0007;
} /* LocalTime */
namespace TimeZoneDatabase {
inline constexpr uint32_t Id = 0x0008;
} /* TimeZoneDatabase */
namespace NTPServerAvailable {
inline constexpr uint32_t Id = 0x0009;
} /* NTPServerAvailable */
namespace TimeZoneListMaxSize {
inline constexpr uint32_t Id = 0x000A;
} /* TimeZoneListMaxSize */
namespace DSTOffsetListMaxSize {
inline constexpr uint32_t Id = 0x000B;
} /* DSTOffsetListMaxSize */
namespace SupportsDNSResolve {
inline constexpr uint32_t Id = 0x000C;
} /* SupportsDNSResolve */
} /* attribute */

namespace command {
namespace SetUTCTime {
inline constexpr uint32_t Id = 0x00;
} /* SetUTCTime */
namespace SetTrustedTimeSource {
inline constexpr uint32_t Id = 0x01;
} /* SetTrustedTimeSource */
namespace SetTimeZone {
inline constexpr uint32_t Id = 0x02;
} /* SetTimeZone */
namespace SetTimeZoneResponse {
inline constexpr uint32_t Id = 0x03;
} /* SetTimeZoneResponse */
namespace SetDSTOffset {
inline constexpr uint32_t Id = 0x04;
} /* SetDSTOffset */
namespace SetDefaultNTP {
inline constexpr uint32_t Id = 0x05;
} /* SetDefaultNTP */
} /* command */

namespace event {
namespace DSTTableEmpty {
inline constexpr uint32_t Id = 0x00;
} /* DSTTableEmpty */
namespace DSTStatus {
inline constexpr uint32_t Id = 0x01;
} /* DSTStatus */
namespace TimeZoneStatus {
inline constexpr uint32_t Id = 0x02;
} /* TimeZoneStatus */
namespace TimeFailure {
inline constexpr uint32_t Id = 0x03;
} /* TimeFailure */
namespace MissingTrustedTimeSource {
inline constexpr uint32_t Id = 0x04;
} /* MissingTrustedTimeSource */
} /* event */

} /* time_synchronization */
} /* cluster */
} /* esp_matter */
