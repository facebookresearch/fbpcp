#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import TestCase
from unittest.mock import MagicMock, patch

from pce.entity.log_group_aws import LogGroup
from pce.gateway.logs_aws import LogsGateway


class TestLogsGateway(TestCase):
    REGION = "us-west-1"
    TEST_LOG_GROUP_NAME = "/ecs/test-log-group-name"
    TEST_LOG_GROUP_ARN = (
        f"arn:aws:logs:{REGION}:123456789012:log-group:{TEST_LOG_GROUP_NAME}:*"
    )
    TEST_ADDITIONAL_LOG_GROUP_NAME = "/ecs/test-log_group-name"
    TEST_ADDITIONAL_LOG_GROUP_ARN = (
        f"arn:aws:logs:{REGION}:123456789012:log-group:{TEST_LOG_GROUP_NAME}:*"
    )

    @patch("boto3.client")
    def setUp(self, mock_boto_client: MagicMock) -> None:
        self.aws_logs = MagicMock()
        mock_boto_client.return_value = self.aws_logs
        self.logs = LogsGateway(region=self.REGION)

    def test_describe_log_group(self) -> None:
        test_log_groups_response = {
            "logGroups": [
                {
                    "logGroupName": self.TEST_LOG_GROUP_NAME,
                    "creationTime": 1640137658065,
                    "metricFilterCount": 0,
                    "arn": self.TEST_LOG_GROUP_ARN,
                    "storedBytes": 0,
                },
                {
                    "logGroupName": self.TEST_ADDITIONAL_LOG_GROUP_NAME,
                    "creationTime": 1633025558042,
                    "metricFilterCount": 0,
                    "arn": self.TEST_ADDITIONAL_LOG_GROUP_ARN,
                    "storedBytes": 980,
                },
            ]
        }
        self.aws_logs.describe_log_groups = MagicMock(
            return_value=test_log_groups_response
        )
        exist_log_group = self.logs.describe_log_group(
            log_group_name=self.TEST_LOG_GROUP_NAME
        )

        expected_log_group = LogGroup(
            log_group_name=self.TEST_LOG_GROUP_NAME,
        )

        self.assertEqual(exist_log_group, expected_log_group)
        self.aws_logs.describe_log_group.assert_called
