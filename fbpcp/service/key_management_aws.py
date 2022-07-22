#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, List, Optional

from fbpcp.gateway.kms import KMSGateway


class AWSKeyManagementService:
    key_id: str
    grant_tokens: List[str]

    def __init__(
        self,
        region: str,
        key_id: str,
        grant_tokens: Optional[List[str]] = None,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Args:
            grant_tokens:   Advertiser side specific, allows anyone with a grant token to have permisions to certain functions on KMS (Admin Controlled)
        """
        self.kms_gateway = KMSGateway(region, access_key_id, access_key_data, config)
        self.key_id = key_id
        self.grant_tokens = grant_tokens if grant_tokens else []
