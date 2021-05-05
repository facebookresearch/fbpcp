#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, List, Optional

import boto3
from fbpcs.entity.vpc_instance import Vpc
from fbpcs.mapper.aws import map_ec2vpc_to_vpcinstance


class EC2Gateway:
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str],
        access_key_data: Optional[str],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.region = region
        config = config or {}

        if access_key_id is not None:
            config["aws_access_key_id"] = access_key_id

        if access_key_data is not None:
            config["aws_secret_access_key"] = access_key_data

        # pyre-ignore
        self.client = boto3.client("ec2", region_name=self.region, **config)

    def describe_vpcs(self, vpc_ids: List[str]) -> List[Vpc]:
        response = self.client.describe_vpcs(VpcIds=vpc_ids)
        return [map_ec2vpc_to_vpcinstance(vpc) for vpc in response["Vpcs"]]

    def describe_vpc(self, vpc_id: str) -> Vpc:
        return self.describe_vpcs([vpc_id])[0]

    def list_vpcs(self) -> List[str]:
        all_vpcs = self.client.describe_vpcs()
        return [vpc["VpcId"] for vpc in all_vpcs["Vpcs"]]
