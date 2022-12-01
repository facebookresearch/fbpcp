#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, Optional

from onedocker.entity.metadata import PackageMetadata
from onedocker.gateway.dynamodb import DynamoDBGateway
from onedocker.mapper.aws import map_dynamodbitem_to_packagemetadata


class MetadataService:
    def __init__(
        self,
        region: str,
        table_name: str,
        key_name: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.table_name = table_name
        self.key_name = key_name
        self.dynamodb_gateway = DynamoDBGateway(
            region, access_key_id, access_key_data, config
        )

    def _build_key(self, package_name: str, version: str) -> str:
        return f"{package_name}#{version}"

    def get_medadata(self, package_name: str, version: str) -> PackageMetadata:
        dynamodb_item = self.dynamodb_gateway.get_item(
            table_name=self.table_name,
            key_name=self.key_name,
            key_value=self._build_key(package_name=package_name, version=version),
        )

        return map_dynamodbitem_to_packagemetadata(dynamodb_item=dynamodb_item)

    def put_metadata(self, metadata: PackageMetadata) -> None:
        md_dict = metadata.to_dict()
        md_dict.update(
            {self.key_name: self._build_key(metadata.package_name, metadata.version)}
        )
        self.dynamodb_gateway.put_item(table_name=self.table_name, item=md_dict)
