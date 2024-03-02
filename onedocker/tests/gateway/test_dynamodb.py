#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import unittest
from unittest.mock import MagicMock, patch

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

from onedocker.gateway.dynamodb import DynamoDBGateway


class TestDynamoGateway(unittest.TestCase):
    TEST_ACCESS_KEY_ID = "test-access-key-id"
    TEST_ACCESS_KEY_DATA = "test-access-key-data"
    TEST_REGION = "us-west-2"
    TEST_TABLE_NAME = "test_table"

    @patch("boto3.client")
    def setUp(self, BotoClient) -> None:
        self.gw = DynamoDBGateway(
            self.TEST_REGION, self.TEST_ACCESS_KEY_ID, self.TEST_ACCESS_KEY_DATA
        )
        self.gw.client = BotoClient()
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    def test_put_item(self) -> None:
        # Arrange
        test_key_name = "instance_id"
        test_key_value = "111"
        test_attribute_name = "instance_name"
        test_attribute_value = "test"
        test_item = {
            test_key_name: test_key_value,
            test_attribute_name: test_attribute_value,
        }
        expected_item = {
            test_key_name: {"S": test_key_value},
            test_attribute_name: {"S": test_attribute_value},
        }

        # Act
        self.gw.put_item(self.TEST_TABLE_NAME, test_item)

        # Assert
        self.gw.client.put_item.assert_called_with(
            TableName=self.TEST_TABLE_NAME,
            Item=expected_item,
            ConditionExpression="attribute_not_exists(instance_id)",
        )

    def test_get_item(self) -> None:
        # Arrange
        test_key_name = "instance_id"
        test_key_value = "111"
        test_attribute_name = "instance_name"
        test_attribute_value = "test"
        client_return = {
            "Item": {
                test_key_name: {"S": test_key_value},
                test_attribute_name: {"S": test_attribute_value},
            },
            "ResponseMetadata": {
                "RequestId": "JSSDCD5NEGJ5VBSI7QO36GENVRVV4KQNSO5AEMVJF66Q9ASUAAJG",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "server": "Server",
                    "date": "Mon, 22 Aug 2022 17:15:26 GMT",
                    "content-type": "application/x-amz-json-1.0",
                    "x-amzn-requestid": "JSSDCD5NEGJ5VBSI7QO36GENVRVV4KQNSO5AEMVJF66Q9ASUAAJG",
                    "x-amz-crc32": "2917446620",
                    "via": "HTTP/1.1 52.94.28.254:443 (fwdproxy2/234c392404618314ed5316cce89d49ae 66.220.149.19)",
                    "x-connected-to": "52.94.28.254",
                    "x-fb-ip-type": "allow_default",
                    "connection": "keep-alive",
                    "content-length": "85",
                },
                "RetryAttempts": 0,
            },
        }
        expected_return = {
            test_key_name: test_key_value,
            test_attribute_name: test_attribute_value,
        }
        self.gw.client.get_item = MagicMock(return_value=client_return)

        # Act
        res = self.gw.get_item(
            table_name=self.TEST_TABLE_NAME,
            key_name=test_key_name,
            key_value=test_key_value,
        )

        # Assert
        self.assertEqual(res, expected_return)

    def test_delete_item(self) -> None:
        # Arrange
        test_key_name = "instance_id"
        test_key_value = "111"
        expected_key = {test_key_name: self.serializer.serialize(test_key_value)}

        # Act
        self.gw.delete_item(
            table_name=self.TEST_TABLE_NAME,
            key_name=test_key_name,
            key_value=test_key_value,
        )

        # Assert
        self.gw.client.delete_item.assert_called_with(
            TableName=self.TEST_TABLE_NAME, Key=expected_key
        )

    def test_update(self):
        # Arrange
        test_key_name = "instance_id"
        test_key_value = "111"
        test_attribute_name = "instance_name"
        test_new_attribute_value = "test_update"
        test_boto3_key = {test_key_name: self.serializer.serialize(test_key_value)}
        test_update_expression = f"SET {test_attribute_name} = :new_data"
        test_boto3_attributes = {
            ":new_data": self.serializer.serialize(test_new_attribute_value)
        }
        # Act
        self.gw.update_item(
            table_name=self.TEST_TABLE_NAME,
            key_name=test_key_name,
            key_value=test_key_value,
            attribute_name=test_attribute_name,
            new_value=test_new_attribute_value,
        )

        # Assert
        self.gw.client.update_item.assert_called_with(
            TableName=self.TEST_TABLE_NAME,
            Key=test_boto3_key,
            UpdateExpression=test_update_expression,
            ExpressionAttributeValues=test_boto3_attributes,
            ConditionExpression="attribute_exists(instance_id)",
        )
