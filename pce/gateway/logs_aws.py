# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, Optional

import boto3
import botocore
from fbpcp.gateway.aws import AWSGateway
from pce.entity.log_group_aws import LogGroup


class LogsGateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)

        self.client: botocore.client.BaseClient = boto3.client(
            "logs", region_name=self.region, **self.config
        )

    def describe_log_group(self, log_group_name: str) -> Optional[LogGroup]:
        response = self.client.describe_log_groups(logGroupNamePrefix=log_group_name)
        """
        Only 1 log group name will be expected in this case
        Though this API returns up to 50 matches and a nextToken is required for pagination,  the first match will be the exact log_group_name
        """
        for group in response["logGroups"]:
            if group["logGroupName"] == log_group_name:
                log_group = LogGroup(log_group_name=group["logGroupName"])
                return log_group
