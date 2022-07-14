#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

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
    def decrypt(
        self,
        key_id: str,
        ciphertext_blob: bytes,
        encryption_context: Dict[str, str],
        grant_tokens: List[str],
        encryption_algorithm: str,
    ) -> Dict[str, Any]:
        return self.client.encrypt(
            KeyId=key_id,
            CiphertextBlob=ciphertext_blob,
            EncryptionContext=encryption_context,
            GrantTokens=grant_tokens,
            EncryptionAlgorithm=encryption_algorithm,
        )

    @error_handler
    def encrypt(
        self,
        key_id: str,
        plaintext: bytes,
        encryption_context: Dict[str, str],
        grant_tokens: List[str],
        encryption_algorithm: str,
    ) -> Dict[str, Any]:
        return self.client.encrypt(
            KeyId=key_id,
            Plaintext=plaintext,
            EncryptionContext=encryption_context,
            GrantTokens=grant_tokens,
            EncryptionAlgorithm=encryption_algorithm,
        )

    @error_handler
    def sign(
        self,
        key_id: str,
        message: bytes,
        message_type: str,
        grant_tokens: List[str],
        signing_algorithm: str,
    ) -> Dict[str, Any]:
        return self.client.sign(
            KeyId=key_id,
            Message=message,
            MessageType=message_type,
            GrantTokens=grant_tokens,
            SigningAlgorithm=signing_algorithm,
        )

    @error_handler
    def verify(
        self,
        key_id: str,
        message: bytes,
        message_type: str,
        signature: bytes,
        signing_algorithm: str,
        grant_tokens: List[str],
    ) -> Dict[str, Any]:
        return self.client.verify(
            KeyId=key_id,
            Message=message,
            MessageType=message_type,
            Signature=signature,
            SigningAlgorithm=signing_algorithm,
            GrantTokens=grant_tokens,
        )
