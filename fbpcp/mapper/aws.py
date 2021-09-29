#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from decimal import Decimal
from typing import Any, Dict, List

from fbpcp.cloud.region import RegionName
from fbpcp.cloud.service import ServiceName
from fbpcp.entity.cloud_cost import CloudCost, CloudCostItem
from fbpcp.entity.cluster_instance import Cluster, ClusterStatus
from fbpcp.entity.container_definition import ContainerDefinition
from fbpcp.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcp.entity.firewall_ruleset import FirewallRule, FirewallRuleset
from fbpcp.entity.route_table import (
    RouteTable,
    Route,
    RouteTarget,
    RouteTargetType,
    RouteState,
)
from fbpcp.entity.subnet import Subnet
from fbpcp.entity.vpc_instance import Vpc, VpcState
from fbpcp.entity.vpc_peering import VpcPeering, VpcPeeringRole, VpcPeeringState
from fbpcp.util.aws import convert_list_to_dict


def map_ecstask_to_containerinstance(task: Dict[str, Any]) -> ContainerInstance:
    container = task["containers"][0]
    ip_v4 = (
        container["networkInterfaces"][0]["privateIpv4Address"]
        if len(container["networkInterfaces"]) > 0
        else None
    )

    status = container["lastStatus"]
    if status == "RUNNING":
        status = ContainerInstanceStatus.STARTED
    elif status == "STOPPED":
        if container.get("exitCode") == 0:
            status = ContainerInstanceStatus.COMPLETED
        else:
            status = ContainerInstanceStatus.FAILED
    else:
        status = ContainerInstanceStatus.UNKNOWN

    return ContainerInstance(task["taskArn"], ip_v4, status)


def map_esccluster_to_clusterinstance(cluster: Dict[str, Any]) -> Cluster:
    status = cluster["status"]
    if status == "ACTIVE":
        status = ClusterStatus.ACTIVE
    elif status == "INACTIVE":
        status = ClusterStatus.INACTIVE
    else:
        status = ClusterStatus.UNKNOWN

    tags = convert_list_to_dict(cluster["tags"], "key", "value")
    return Cluster(
        cluster_arn=cluster["clusterArn"],
        cluster_name=cluster["clusterName"],
        pending_tasks=cluster["pendingTasksCount"],
        running_tasks=cluster["runningTasksCount"],
        status=status,
        tags=tags,
    )


def map_ec2vpc_to_vpcinstance(vpc: Dict[str, Any]) -> Vpc:
    state = vpc["State"]
    if state == "pending":
        state = VpcState.PENDING
    elif state == "available":
        state = VpcState.AVAILABLE
    else:
        state = VpcState.UNKNOWN

    vpc_id = vpc["VpcId"]
    cidr_block = vpc["CidrBlock"]
    # some vpc instances don't have any tags
    tags = convert_list_to_dict(vpc["Tags"], "Key", "Value") if "Tags" in vpc else {}

    # TODO add implementation to get the firewall_ruleset
    return Vpc(vpc_id, cidr_block, state, tags)


def map_ec2subnet_to_subnet(subnet: Dict[str, Any]) -> Subnet:
    availability_zone = subnet["AvailabilityZone"]
    subnet_id = subnet["SubnetId"]
    tags = (
        convert_list_to_dict(subnet["Tags"], "Key", "Value") if "Tags" in subnet else {}
    )
    return Subnet(subnet_id, availability_zone, tags)


def map_cecost_to_cloud_cost(cost_by_date: List[Dict[str, Any]]) -> CloudCost:
    total_cost_amount = Decimal(0)
    cost_items = {}
    for daily_result in cost_by_date:
        for group_result in daily_result.get("Groups"):
            amount = Decimal(group_result["Metrics"]["UnblendedCost"]["Amount"])
            total_cost_amount += amount
            cost_items[tuple(group_result["Keys"])] = (
                cost_items.get(tuple(group_result["Keys"]), 0) + amount
            )

    return CloudCost(
        total_cost_amount=total_cost_amount,
        details=[
            CloudCostItem(
                region=RegionName(region),
                service=ServiceName(service),
                cost_amount=amount,
            )
            for (region, service), amount in cost_items.items()
        ],
    )


def map_ec2route_to_route(route: Dict[str, Any]) -> Route:
    destination_cidr = route["DestinationCidrBlock"]
    route_target_type = RouteTargetType.OTHER
    route_target_id = ""
    if "VpcPeeringConnectionId" in route:
        route_target_type = RouteTargetType.VPC_PEERING
        route_target_id = route["VpcPeeringConnectionId"]
    elif "GatewayId" in route:
        route_target_type = RouteTargetType.INTERNET
        route_target_id = route["GatewayId"]
    state = RouteState.UNKNOWN
    if route["State"] == "active":
        state = RouteState.ACTIVE
    route_target = RouteTarget(route_target_id, route_target_type)
    return Route(destination_cidr, route_target, state)


def map_ec2routetable_to_routetable(route_table: Dict[str, Any]) -> RouteTable:
    route_table_id = route_table["RouteTableId"]
    routes = [map_ec2route_to_route(route) for route in route_table["Routes"]]
    vpc_id = route_table["VpcId"]
    tags = (
        convert_list_to_dict(route_table["Tags"], "Key", "Value")
        if "Tags" in route_table
        else {}
    )
    return RouteTable(route_table_id, routes, vpc_id, tags)


def map_ec2ippermission_to_firewallrule(ip_permission: Dict[str, Any]) -> FirewallRule:
    ip_protocol = ip_permission["IpProtocol"]
    from_port = ip_permission["FromPort"] if "FromPort" in ip_permission else -1
    to_port = ip_permission["ToPort"] if "ToPort" in ip_permission else -1
    ip_range = ip_permission["IpRanges"][0]
    cidr = ip_range["CidrIp"]
    return FirewallRule(from_port, to_port, ip_protocol, cidr)


def map_ec2securitygroup_to_firewallruleset(
    security_group: Dict[str, Any]
) -> FirewallRuleset:
    id = security_group["GroupId"]
    vpc_id = security_group["VpcId"]
    tags = (
        convert_list_to_dict(security_group["Tags"], "Key", "Value")
        if "Tags" in security_group
        else {}
    )
    ingress = [
        map_ec2ippermission_to_firewallrule(ip_permission)
        for ip_permission in security_group["IpPermissions"]
    ]
    egress = [
        map_ec2ippermission_to_firewallrule(ip_permission)
        for ip_permission in security_group["IpPermissionsEgress"]
    ]
    return FirewallRuleset(id, vpc_id, ingress, egress, tags)


def map_ec2vpcpeering_to_vpcpeering(
    vpc_peering: Dict[str, Any], vpc_id: str
) -> VpcPeering:
    id = vpc_peering["VpcPeeringConnectionId"]
    status = VpcPeeringState.NOT_READY
    status_code = vpc_peering["Status"]["Code"]
    if status_code == "active":
        status = VpcPeeringState.ACTIVE
    elif status_code == "pending-acceptance":
        status = VpcPeeringState.PENDING_ACCEPTANCE
    elif status_code == "rejected":
        status = VpcPeeringState.REJECTED
    requester_vpc_id = vpc_peering["RequesterVpcInfo"]["VpcId"]
    accepter_vpc_id = vpc_peering["AccepterVpcInfo"]["VpcId"]
    role = (
        VpcPeeringRole.REQUESTER
        if requester_vpc_id == vpc_id
        else VpcPeeringRole.ACCEPTER
    )
    tags = (
        convert_list_to_dict(vpc_peering["Tags"], "Key", "Value")
        if "Tags" in vpc_peering
        else {}
    )
    return VpcPeering(id, status, role, requester_vpc_id, accepter_vpc_id, tags)


def map_ecstaskdefinition_to_containerdefinition(
    task_definition: Dict[str, Any],
    tag_list: List[Dict[str, str]],
) -> ContainerDefinition:
    task_definition_id = task_definition["taskDefinitionArn"]
    container_definition = task_definition["containerDefinitions"][0]
    image = container_definition["image"]
    cpu = (
        container_definition["cpu"]
        if "cpu" in container_definition
        else task_definition["cpu"]
    )
    memory = (
        container_definition["memory"]
        if "memory" in container_definition
        else task_definition["memory"]
    )
    entry_point = (
        container_definition["entryPoint"]
        if "entryPoint" in container_definition
        else []
    )
    environment = convert_list_to_dict(
        container_definition["environment"], "name", "value"
    )
    task_role_id = task_definition["taskRoleArn"]
    tags = convert_list_to_dict(tag_list, "key", "value")
    return ContainerDefinition(
        task_definition_id,
        image,
        cpu,
        memory,
        entry_point,
        environment,
        task_role_id,
        tags,
    )
