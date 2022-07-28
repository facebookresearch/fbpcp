#!/usr/bin/env fbpython
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.service.key_management_aws import AWSKeyManagementService


class TestAWSKeyManagementService(unittest.TestCase):
    REGION = "us-west-2"

    TEST_KEY_ID = "test-key-id"
    TEST_SIGNING_ALGORITHM = "test-signing-algorithm"

    TEST_ACCESS_KEY_ID = "test-access-key-id"
    TEST_ACCESS_KEY_DATA = "test-access-key-data"

    @patch("boto3.client")
    def setUp(self, BotoClient) -> None:
        self.kms_aws = AWSKeyManagementService(
            region=self.REGION,
            key_id=self.TEST_KEY_ID,
            signing_algorithm=self.TEST_SIGNING_ALGORITHM,
            access_key_id=self.TEST_ACCESS_KEY_ID,
            access_key_data=self.TEST_ACCESS_KEY_DATA,
        )
        self.kms_aws.kms_gateway.client = BotoClient()

    def test_sign(self) -> None:
        # Arrange
        sign_args = {
            "message": "test_message",
            "message_type": "test_message_type",
        }
        signed_message = "test_signed_message"

        self.kms_aws.kms_gateway.sign = MagicMock(return_value=signed_message)

        # Act
        signature = self.kms_aws.sign(**sign_args)

        # Assert
        self.assertEqual(signature, signed_message)
