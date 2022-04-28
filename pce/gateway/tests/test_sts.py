#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from pce.gateway.sts import STSGateway


class TestSTSGateway(TestCase):
    REGION = "us-west-2"
    TEST_AWS_ACCOUNT_ID = "123456789012"

    def setUp(self) -> None:
        self.aws_sts = MagicMock()
        with patch("boto3.client") as mock_client:
            mock_client.return_value = self.aws_sts
            self.sts = STSGateway(self.REGION)

    def test_get_caller_arn(self) -> None:
        # Arrange
        client_return_response = {
            "UserId": "userID",
            "Account": "123456789012",
            "Arn": "foo",
        }

        self.aws_sts.get_caller_identity = MagicMock(
            return_value=client_return_response
        )

        expected_arn = "foo"

        # Act
        arn = self.sts.get_caller_arn()

        # Assert
        self.assertEqual(expected_arn, arn)
        self.aws_sts.get_caller_identity.assert_called()
