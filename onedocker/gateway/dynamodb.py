#!/usr/bin/env python3
# Copyright (c) Meta, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, Optional

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.exceptions import ClientError
from fbpcp.decorator.error_handler import error_handler
from fbpcp.error.pcp import PcpError
from fbpcp.gateway.aws import AWSGateway


class DynamoDBGateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)
        # pyre-ignore
        self.client = boto3.client("dynamodb", region_name=self.region, **self.config)
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    @error_handler
    def put_item(self, table_name: str, item: Dict[str, Any]) -> None:
        dynamo_item = {k: self.serializer.serialize(v) for k, v in item.items()}
        try:
            self.client.put_item(
                TableName=table_name,
                Item=dynamo_item,
                ConditionExpression="attribute_not_exists(instance_id)",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise PcpError(
                    "Cannot put item, an item with the given instance_id already exists"
                )
            raise e

    @error_handler
    def get_item(
        self,
        table_name: str,
        key_name: str,
        # pyre-ignore
        key_value: Any,
    ) -> Dict[str, Any]:
        key = {key_name: self.serializer.serialize(key_value)}
        raw_response = self.client.get_item(
            TableName=table_name,
            Key=key,
        )
        if "Item" not in raw_response:
            raise PcpError(f"No item in database for key {key_name}: {key_value}")
        return {
            k: self.deserializer.deserialize(v) for k, v in raw_response["Item"].items()
        }

    @error_handler
    def update_item(
        self,
        table_name: str,
        key_name: str,
        # pyre-ignore
        key_value: Any,
        attribute_name: str,
        # pyre-ignore
        new_value: Any,
    ) -> None:
        update_expression = f"SET {attribute_name} = :new_data"
        expression_attributes = {":new_data": new_value}
        boto3_key = {key_name: self.serializer.serialize(key_value)}
        boto3_attributes = {
            k: self.serializer.serialize(v) for k, v in expression_attributes.items()
        }
        try:
            self.client.update_item(
                TableName=table_name,
                Key=boto3_key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=boto3_attributes,
                ConditionExpression="attribute_exists(instance_id)",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise PcpError(
                    "Cannot get item, an item with the given instance_id does not already exist"
                )
            raise e

    @error_handler
    def delete_item(
        self,
        table_name: str,
        key_name: str,
        # pyre-ignore
        key_value: Any,
    ) -> None:
        boto3_key = {key_name: self.serializer.serialize(key_value)}
        self.client.delete_item(TableName=table_name, Key=boto3_key)
