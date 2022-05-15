# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, Optional

import boto3
import botocore
from fbpcp.gateway.aws import AWSGateway
from fbpcp.util.aws import split_container_definition
from pce.mapper.aws import map_ecstaskdefinition_to_awslogsgroupname


class ECSGateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)

        self.client: botocore.client.BaseClient = boto3.client(
            "ecs", region_name=self.region, **self.config
        )

    def extract_log_group_name(self, container_definition_id: str) -> Optional[str]:
        task_definition_arn = split_container_definition(container_definition_id)[0]

        response = self.client.describe_task_definition(
            taskDefinition=task_definition_arn
        )
        log_group_name = map_ecstaskdefinition_to_awslogsgroupname(
            response["taskDefinition"]
        )
        return log_group_name
