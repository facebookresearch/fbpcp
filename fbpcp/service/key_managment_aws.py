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
    signing_algorithm: str
    grant_tokens: List[str]

    def __init__(
        self,
        region: str,
        key_id: str,
        signing_algorithm: Optional[str] = None,
        grant_tokens: Optional[List[str]] = None,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.kms_gateway = KMSGateway(region, access_key_id, access_key_data, config)
        self.key_id = key_id
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
