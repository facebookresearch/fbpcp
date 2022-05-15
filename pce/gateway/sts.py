# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, Optional

import boto3
from fbpcp.gateway.aws import AWSGateway


class STSGateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)

        # pyre-ignore
        self.client = boto3.client("sts", region_name=self.region, **self.config)

    def get_caller_arn(
        self,
    ) -> str:
        response = self.client.get_caller_identity()

        return response["Arn"]
