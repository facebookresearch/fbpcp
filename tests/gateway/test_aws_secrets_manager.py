#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import unittest
from unittest.mock import patch

from botocore.exceptions import ClientError

from fbpcp.entity.secret import StringSecret
from fbpcp.error.pcp import PcpError

from fbpcp.gateway.secrets_manager import AWSSecretsManagerGateway


class TestAWSSecretsManagerGateway(unittest.TestCase):
    @patch("boto3.client")
    def setUp(self, BotoClient) -> None:
        self.gw = AWSSecretsManagerGateway("us-west-2")
        self.gw.client = BotoClient()
        self.secret_id = "test_id"
        self.secret_name = "test_secret_name"
        self.secret_value = "test_secret_value"
        self.tags = {"key1": "value1", "key2": "value2"}
        self.aws_tag_list = [
            {"Key": "key1", "Value": "value1"},
            {"Key": "key2", "Value": "value2"},
        ]
        self.client_error = ClientError(
            error_response={
                "Error": {"Code": 123, "Message": "test"},
                "ResponseMetadata": {},
            },
            operation_name="test_operation",
        )

    def test_create_secret(self):
        # Arrange
        full_resp = {"ARN": self.secret_id}
        self.gw.client.create_secret.return_value = full_resp

        # Act
        resp = self.gw.create_secret(self.secret_name, self.secret_value, self.tags)

        # Assert
        self.gw.client.create_secret.assert_called_with(
            Name=self.secret_name,
            SecretString=self.secret_value,
            Tags=self.aws_tag_list,
        )
        self.assertEqual(self.secret_id, resp)

    def test_create_secret_throw(self):
        # Arrange
        self.gw.client.create_secret.side_effect = self.client_error

        # Act & Assert
        with self.assertRaises(PcpError):
            self.gw.create_secret(self.secret_name, self.secret_value)

    def test_get_secret(self):
        # Arrange
        date = "03-08-2023"
        descr_resp = {
            "ARN": self.secret_id,
            "Name": self.secret_name,
            "CreatedDate": date,
            "Tags": self.aws_tag_list,
        }
        val_resp = {"SecretString": self.secret_value}
        expected_result = StringSecret(
            id=self.secret_id,
            name=self.secret_name,
            value=self.secret_value,
            create_date=date,
            tags=self.tags,
        )
        self.gw.client.get_secret_value.return_value = val_resp
        self.gw.client.describe_secret.return_value = descr_resp

        # Act
        resp = self.gw.get_secret(self.secret_id)

        # Assert
        self.assertEqual(resp, expected_result)
        self.gw.client.get_secret_value.assert_called_with(SecretId=self.secret_id)
        self.gw.client.describe_secret(SecretId=self.secret_id)

    def test_get_secret_throw(self):
        # Arrange
        self.gw.client.get_secret_value.side_effect = self.client_error

        # Act & Assert
        with self.assertRaises(PcpError):
            self.gw.get_secret(self.secret_id)

    def test_delete_secret(self):
        # Act
        self.gw.delete_secret(self.secret_id)

        # Assert
        self.gw.client.delete_secret.assert_called_with(SecretId=self.secret_id)

    def test_delete_secret_throw(self):
        # Arrange
        self.gw.client.delete_secret.side_effect = self.client_error

        # Act & Assert
        with self.assertRaises(PcpError):
            self.gw.delete_secret(self.secret_name, self.secret_value)
