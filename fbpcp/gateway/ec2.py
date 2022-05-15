#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, List, Optional

import boto3
from fbpcp.decorator.error_handler import error_handler
from fbpcp.entity.firewall_ruleset import FirewallRuleset
from fbpcp.entity.route_table import RouteTable
from fbpcp.entity.subnet import Subnet
from fbpcp.entity.vpc_instance import Vpc
from fbpcp.entity.vpc_peering import VpcPeering
from fbpcp.gateway.aws import AWSGateway
from fbpcp.mapper.aws import (
    map_ec2routetable_to_routetable,
    map_ec2securitygroup_to_firewallruleset,
    map_ec2subnet_to_subnet,
    map_ec2vpc_to_vpcinstance,
    map_ec2vpcpeering_to_vpcpeering,
)
from fbpcp.util.aws import convert_vpc_tags_to_filter


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

    @error_handler
    def describe_vpcs(
        self,
        vpc_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[Vpc]:
        if vpc_ids is None:
            vpc_ids = []
        filters = convert_vpc_tags_to_filter(tags)
        response = self.client.describe_vpcs(VpcIds=vpc_ids, Filters=filters)
        return [map_ec2vpc_to_vpcinstance(vpc) for vpc in response["Vpcs"]]

    @error_handler
    def describe_vpc(self, vpc_id: str) -> Vpc:
        return self.describe_vpcs([vpc_id])[0]

    @error_handler
    def list_vpcs(self) -> List[str]:
        all_vpcs = self.client.describe_vpcs()
        return [vpc["VpcId"] for vpc in all_vpcs["Vpcs"]]

    @error_handler
    def describe_subnets(
        self,
        vpc_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[Subnet]:
        filters = convert_vpc_tags_to_filter(tags, vpc_id)
        response = self.client.describe_subnets(Filters=filters)
        return [map_ec2subnet_to_subnet(subnet) for subnet in response["Subnets"]]

    @error_handler
    def describe_route_tables(
        self,
        vpc_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[RouteTable]:
        filters = convert_vpc_tags_to_filter(tags, vpc_id)
        response = self.client.describe_route_tables(Filters=filters)
        return [
            map_ec2routetable_to_routetable(route_table)
            for route_table in response["RouteTables"]
        ]

    @error_handler
    def describe_security_groups(
        self,
        vpc_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[FirewallRuleset]:
        filters = convert_vpc_tags_to_filter(tags, vpc_id)
        response = self.client.describe_security_groups(Filters=filters)
        return [
            map_ec2securitygroup_to_firewallruleset(security_group)
            for security_group in response["SecurityGroups"]
        ]

    @error_handler
    def describe_vpc_peerings(
        self,
        vpc_id: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[VpcPeering]:
        filters = convert_vpc_tags_to_filter(tags)
        response = self.client.describe_vpc_peering_connections(Filters=filters)
        return [
            map_ec2vpcpeering_to_vpcpeering(vpc_peering, vpc_id)
            for vpc_peering in response["VpcPeeringConnections"]
        ]
