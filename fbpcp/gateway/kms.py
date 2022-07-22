#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from base64 import b64decode, b64encode
from typing import Any, Dict, List, Optional

import boto3
from botocore.client import BaseClient
from fbpcp.decorator.error_handler import error_handler
from fbpcp.gateway.aws import AWSGateway


class KMSGateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)
        self.client: BaseClient = boto3.client(
            "kms", region_name=self.region, **self.config
        )

    @error_handler
    def sign(
        self,
        key_id: str,
        message: str,
        message_type: str,
        grant_tokens: List[str],
        signing_algorithm: str,
    ) -> str:
        response = self.client.sign(
            KeyId=key_id,
            Message=message.encode(),
            MessageType=message_type,
            GrantTokens=grant_tokens,
            SigningAlgorithm=signing_algorithm,
        )
        signature = b64encode(response["Signature"]).decode()
        return signature

    @error_handler
    def verify(
        self,
        key_id: str,
        message: str,
        message_type: str,
        signature: str,
        signing_algorithm: str,
        grant_tokens: List[str],
    ) -> bool:
        b64_signature = b64decode(signature.encode())
        response = self.client.verify(
            KeyId=key_id,
            Message=message.encode(),
            MessageType=message_type,
            Signature=b64_signature,
            SigningAlgorithm=signing_algorithm,
            GrantTokens=grant_tokens,
        )
        return response["SignatureValid"]
