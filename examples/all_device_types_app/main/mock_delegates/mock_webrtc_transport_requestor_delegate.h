/*
   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/

#pragma once

#include <app/clusters/webrtc-transport-requestor-server/webrtc-transport-requestor-cluster.h>
#include <protocols/interaction_model/StatusCode.h>

/*
 * Mock WebRTCTransportRequestor Delegate Implementation
 * This file provides a mock implementation of the WebRTCTransportRequestor::Delegate interface
 * that returns success for all methods.
 * For more details, take a look at the delegate interface in the Matter SDK.
 * 1. Delegate Interface: https://github.com/project-chip/connectedhomeip/blob/d144bbb/src/app/clusters/webrtc-transport-requestor-server/webrtc-transport-requestor-cluster.h
 */

namespace chip {
namespace app {
namespace Clusters {
namespace WebRTCTransportRequestor {

class MockWebRTCTransportRequestorDelegate : public Delegate
{
public:
    MockWebRTCTransportRequestorDelegate() : Delegate() {}
    virtual ~MockWebRTCTransportRequestorDelegate() = default;

    // WebRTC transport requestor handlers
    CHIP_ERROR HandleOffer(uint16_t sessionId, const OfferArgs & args) override;
    CHIP_ERROR HandleAnswer(uint16_t sessionId, const std::string & sdpAnswer) override;
    CHIP_ERROR HandleICECandidates(uint16_t sessionId, const std::vector<ICECandidateStruct> & candidates) override;
    CHIP_ERROR HandleEnd(uint16_t sessionId, WebRTCEndReasonEnum reasonCode) override;

private:
    static constexpr const char * LOG_TAG = "MockWebRTCTransportRequestorDelegate";
};

} // namespace WebRTCTransportRequestor
} // namespace Clusters
} // namespace app
} // namespace chip

