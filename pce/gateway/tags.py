# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, List, Optional

import boto3
import botocore
from fbpcp.decorator.error_handler import error_handler
from fbpcp.error.pcp import PcpError
from fbpcp.gateway.aws import AWSGateway


class TagsGateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)

        self.client: botocore.client.BaseClient = boto3.client(
            "resourcegroupstaggingapi", region_name=self.region, **self.config
        )

    @error_handler
    def tag_resources(self, resource_arn_list: List[str], tags: Dict[str, str]) -> None:
        response = self.client.tag_resources(
            ResourceARNList=resource_arn_list, Tags=tags
        )
        failures = response["FailedResourcesMap"]
        if failures:
            raise PcpError(f"Tagging unsuccessful. Failed Resources: {failures}")

    @error_handler
    def untag_resources(
        self, resource_arn_list: List[str], tag_keys: List[str]
    ) -> None:
        response = self.client.untag_resources(
            ResourceARNList=resource_arn_list, TagKeys=tag_keys
        )
        failures = response["FailedResourcesMap"]
        if failures:
            raise PcpError(f"Untagging unsuccessful. Failed Resources: {failures}")

    @error_handler
    def get_resources_for_tag(self, tag_name: str, tag_value: str) -> List[str]:
        """Returns the resource ARNs for the resources matching the given tag name and value (upto 100)"""

        tag_filter = {"Key": tag_name, "Values": [tag_value]}
        response = self.client.get_resources(TagFilters=[tag_filter])
        resource_arn_list = [
            resource["ResourceARN"] for resource in response["ResourceTagMappingList"]
        ]
        return resource_arn_list
