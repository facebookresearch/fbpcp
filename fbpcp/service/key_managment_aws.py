#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from base64 import b64encode
from typing import Any, Dict, List, Optional

from fbpcp.gateway.kms import KMSGateway
from fbpcp.service.key_management import KeyManagmentService


class AWSKeyManagmentService(KeyManagmentService):
    key_id: str
    encryption_algorithm: str
    signing_algorithm: str
    grant_tokens: List[str]

    def __init__(
        self,
        region: str,
        key_id: str,
        encryption_algorithm: Optional[str] = None,
        signing_algorithm: Optional[str] = None,
        grant_tokens: Optional[List[str]] = None,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.kms_gateway = KMSGateway(
            region=region,
            access_key_id=access_key_id,
            access_key_data=access_key_data,
            config=config,
        )
        self.key_id = key_id

        self.encryption_algorithm = encryption_algorithm if encryption_algorithm else ""
        self.signing_algorithm = signing_algorithm if signing_algorithm else ""
        self.grant_tokens = grant_tokens if grant_tokens else []

    def sign(self, message: str, message_type: str = "RAW") -> str:
        if not self.signing_algorithm:
            raise ValueError("No Signing Algorithm Set")
        response = self.kms_gateway.sign(
            key_id=self.key_id,
            message=message,
            message_type=message_type,
            grant_tokens=self.grant_tokens,
            signing_algorithm=self.signing_algorithm,
        )
        signature = b64encode(response["Signature"]).decode()
        return signature

    def encrypt(
        self, plaintext: str, encryption_context: Optional[Dict[str, str]] = None
    ) -> str:
        if not self.encryption_algorithm:
            raise ValueError("No Encryption Algorithm Set")
        response = self.kms_gateway.encrypt(
            key_id=self.key_id,
            plaintext=plaintext,
            encryption_context=encryption_context if encryption_context else {},
            grant_tokens=self.grant_tokens,
            encryption_algorithm=self.encryption_algorithm,
        )
        ciphertext_blob = b64encode(response["CiphertextBlob"]).decode()
        return ciphertext_blob
