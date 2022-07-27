#!/usr/bin/env fbpython
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import base64 as b64
import unittest
from unittest.mock import MagicMock, patch

from fbpcp.gateway.kms import KMSGateway


class TestKMSGateway(unittest.TestCase):
    REGION = "us-west-2"
    TEST_ACCESS_KEY_ID = "test-access-key-id"
    TEST_ACCESS_KEY_DATA = "test-access-key-data"

    @patch("boto3.client")
    def setUp(self, BotoClient) -> None:
        self.kms = KMSGateway(
            region=self.REGION,
            access_key_id=self.TEST_ACCESS_KEY_ID,
            access_key_data=self.TEST_ACCESS_KEY_DATA,
        )
        self.kms.client = BotoClient()

    def test_sign(self) -> None:
        # Arrange
        sign_args = {
            "key_id": "test_key_id",
            "message": "test_message",
            "message_type": "test_message_type",
            "grant_tokens": [],
            "signing_algorithm": "",
        }
        signed_message = "test_signed_message"
        self.kms.client.sign = MagicMock(
            return_value={"Signature": signed_message.encode()}
        )

        # Act
        b64_signature = self.kms.sign(**sign_args)
        signature = b64.b64decode(b64_signature.encode()).decode()

        # Assert
        self.assertEqual(signature, signed_message)
