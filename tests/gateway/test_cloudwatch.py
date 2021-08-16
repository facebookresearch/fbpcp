#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.entity.log_event import LogEvent
from fbpcp.gateway.cloudwatch import CloudWatchGateway


class TestCloudWatchGateway(unittest.TestCase):
    REGION = "us-west-1"
    GROUP_NAME = "test-group-name"
    STREAM_NAME = "test-stream-name"

    @patch("boto3.client")
    def test_get_log_events(self, BotoClient):
        gw = CloudWatchGateway(self.REGION)
        mocked_log = {"events": [{"timestamp": 1, "message": "log"}]}
        gw.client = BotoClient()
        gw.client.get_log_events = MagicMock(return_value=mocked_log)
        returned_log = gw.get_log_events(self.GROUP_NAME, self.STREAM_NAME)
        gw.client.get_log_events.assert_called()
        self.assertEqual([LogEvent(1, "log")], returned_log)
