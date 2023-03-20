#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from functools import reduce
from typing import Any, Dict, List, Optional

import boto3
from botocore.client import BaseClient
from fbpcp.decorator.error_handler import error_handler
from fbpcp.entity.secret import StringSecret
from fbpcp.gateway.aws import AWSGateway
from fbpcp.util.aws import convert_list_to_dict


class AWSSecretsManagerGateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)
        self.client: BaseClient = boto3.client(
            "secretsmanager", region_name=self.region, **self.config
        )

    @error_handler
    def create_secret(
        self,
        secret_name: str,
        secret_value: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Returns the id (ARN) of the created secret
        """
        tags_dict = []
        if tags:
            tags_dict = self._generate_tags_dict(tags)

        response = self.client.create_secret(
            Name=secret_name, SecretString=secret_value, Tags=tags_dict
        )
        return response["ARN"]

    @error_handler
    def get_secret(
        self,
        secret_id: str,
    ) -> StringSecret:
        # Get secret value.
        # It retrieves the current version of the secret.
        val_response = self.client.get_secret_value(SecretId=secret_id)
        # Get secret details. E.g tags
        descr_response = self.client.describe_secret(SecretId=secret_id)

        return self._convert_resp_to_secret(descr_response, val_response)

    @error_handler
    def delete_secret(
        self,
        secret_id: str,
    ) -> None:
        # Delete secret.
        self.client.delete_secret(SecretId=secret_id)

    def _convert_resp_to_secret(
        self, descr_resp: Dict[str, Any], val_resp: Dict[str, Any]
    ) -> StringSecret:
        """
        Encapsulate the responses into a Secret object
        """
        id = descr_resp["ARN"]
        name = descr_resp["Name"]
        value = val_resp.get("SecretString")
        create_date = descr_resp.get("CreatedDate")
        tags = convert_list_to_dict(descr_resp.get("Tags"), "Key", "Value")

        return StringSecret(
            id=id, name=name, value=value, create_date=create_date, tags=tags
        )

    def _generate_tags_dict(self, tags: Dict[str, str]) -> List[Dict[str, str]]:
        # Input tag format {"tag1": "v1", "tag2", "v2", ...}
        # AWS required format [{"Key": "tag1", "Value": "v1"}, ...}
        new_dict = reduce(
            lambda x, y: [*x, {"Key": y, "Value": tags[y]}], tags.keys(), []
        )

        return new_dict
