# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, List, Optional

import boto3
from fbpcp.entity.vpc_peering import VpcPeering
from fbpcp.gateway.aws import AWSGateway
from fbpcp.mapper.aws import map_ec2vpcpeering_to_vpcpeering


class EC2Gateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)

        # pyre-ignore
        self.client = boto3.client("ec2", region_name=self.region, **self.config)

    def describe_availability_zones(
        self,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        response = self.client.describe_availability_zones()

        return [aws_az["ZoneName"] for aws_az in response["AvailabilityZones"]]

    def describe_vpc_peering_connections_with_accepter_vpc_id(
        self,
        vpc_id: str,
    ) -> Optional[VpcPeering]:
        filters = [
            {"Name": "accepter-vpc-info.vpc-id", "Values": [vpc_id]},
        ]
        response = self.client.describe_vpc_peering_connections(Filters=filters)
        return (
            map_ec2vpcpeering_to_vpcpeering(
                response["VpcPeeringConnections"][0], vpc_id
            )
            if response["VpcPeeringConnections"]
            else None
        )
