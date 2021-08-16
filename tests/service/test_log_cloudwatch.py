#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.service.log_cloudwatch import CloudWatchLogService

REGION = "us-west-1"
LOG_GROUP = "test-group-name"
LOG_PATH = "test-log-path"


class TestCloudWatchLogService(unittest.TestCase):
    @patch("fbpcp.gateway.cloudwatch.CloudWatchGateway")
    def test_fetch(self, MockCloudWatchGateway):
        log_service = CloudWatchLogService(LOG_GROUP, REGION)
        mocked_log = {"test-events": [{"test-event-name": "test-event-data"}]}
        log_service.cloudwatch_gateway = MockCloudWatchGateway()
        log_service.cloudwatch_gateway.fetch = MagicMock(return_value=mocked_log)
        returned_log = log_service.cloudwatch_gateway.fetch(LOG_PATH)
        log_service.cloudwatch_gateway.fetch.assert_called()
        self.assertEqual(mocked_log, returned_log)
