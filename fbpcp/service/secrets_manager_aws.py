#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import asyncio

from typing import Any, Dict, Optional

from fbpcp.entity.secret import StringSecret

from fbpcp.gateway.secrets_manager import AWSSecretsManagerGateway
from fbpcp.service.secrets_manager import SecretsManagerService


class AWSSecretsManagerService(SecretsManagerService):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.secret_gateway = AWSSecretsManagerGateway(
            region, access_key_id, access_key_data, config
        )

    def create_secret(
        self,
        secret_name: str,
        secret_value: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        secret_id = self.secret_gateway.create_secret(
            secret_name=secret_name, secret_value=secret_value, tags=tags
        )

        return secret_id

    def get_secret(
        self,
        secret_id: str,
    ) -> StringSecret:
        # secret id can be ARN or secret name
        secret = self.secret_gateway.get_secret(secret_id=secret_id)

        return secret

    async def create_secret_async(
        self,
        secret_name: str,
        secret_value: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, self.create_secret, secret_name, secret_value, tags
        )
        return result

    async def get_secret_async(self, secret_id: str) -> StringSecret:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self.get_secret, secret_id)
        return result

    def delete_secret(self, secret_id: str) -> None:
        self.secret_gateway.delete_secret(secret_id=secret_id)

    async def delete_secret_async(self, secret_id: str) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.delete_secret, secret_id)
