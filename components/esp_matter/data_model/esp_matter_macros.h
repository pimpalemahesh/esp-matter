// Copyright 2021 Espressif Systems (Shanghai) PTE LTD
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

#pragma once

#define CALL_ONCE(cb)                           \
    [](){                                       \
        static bool is_called = false;          \
        if (!is_called) {                       \
            cb();                               \
            is_called = true;                   \
        }                                       \
    }

// convenience macro for checking if features is enabled or not
// must be used only from the ::create() API so that it can find config
// eg: if (has(feature::constant_pressure)) { ... }
#define has(flags) ((config->feature_flags & flags) ? 1 : 0)

// Macros to reduce repetitive validation code
#define VALIDATE_FEATURES_EXACT_ONE(name, ...) \
    do { if (!validate_features(config->feature_flags, feature_policy::k_exact_one, name, {__VA_ARGS__})) \
        return ABORT_CLUSTER_CREATE(cluster); } while(0)

#define VALIDATE_FEATURES_AT_LEAST_ONE(name, ...) \
    do { if (!validate_features(config->feature_flags, feature_policy::k_at_least_one, name, {__VA_ARGS__})) \
        return ABORT_CLUSTER_CREATE(cluster); } while(0)
