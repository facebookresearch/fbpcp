#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from decimal import Decimal
from typing import Any, Dict, List

from fbpcp.entity.cloud_cost import CloudCost, CloudCostItem
from fbpcp.entity.cluster_instance import Cluster, ClusterStatus
from fbpcp.entity.container_definition import ContainerDefinition
from fbpcp.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcp.entity.firewall_ruleset import FirewallRule, FirewallRuleset
from fbpcp.entity.policy_statement import PolicyStatement
from fbpcp.entity.route_table import (
    Route,
    RouteState,
    RouteTable,
    RouteTarget,
    RouteTargetType,
)
from fbpcp.entity.subnet import Subnet
from fbpcp.entity.vpc_instance import Vpc, VpcState
from fbpcp.entity.vpc_peering import VpcPeering, VpcPeeringRole, VpcPeeringState
from fbpcp.util.aws import (
    convert_list_to_dict,
    convert_obj_to_list,
    get_container_definition_id,
    get_json_values,
)


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
    tags = convert_list_to_dict(vpc.get("Tags"), "Key", "Value")

    # TODO add implementation to get the firewall_ruleset
    return Vpc(vpc_id, cidr_block, state, tags)


def map_ec2subnet_to_subnet(subnet: Dict[str, Any]) -> Subnet:
    availability_zone = subnet["AvailabilityZone"]
    subnet_id = subnet["SubnetId"]
    tags = convert_list_to_dict(subnet.get("Tags"), "Key", "Value")
    return Subnet(subnet_id, availability_zone, tags)


def map_cecost_to_cloud_cost(cost_by_date: List[Dict[str, Any]]) -> CloudCost:
    total_cost_amount = Decimal(0)
    cost_items = {}
    for daily_result in cost_by_date:
        for group_result in daily_result.get("Groups"):
            amount = Decimal(group_result["Metrics"]["UnblendedCost"]["Amount"])
            total_cost_amount += amount
            cost_items[group_result["Keys"][0]] = (
                cost_items.get(group_result["Keys"][0], 0) + amount
            )

    return CloudCost(
        total_cost_amount=total_cost_amount,
        details=[
            CloudCostItem(
                service=service,
                cost_amount=amount,
            )
            for service, amount in cost_items.items()
        ],
    )


def map_ec2route_to_route(route: Dict[str, Any]) -> Route:
    destination_cidr = route["DestinationCidrBlock"]
    route_target_type = RouteTargetType.OTHER
    route_target_id = ""
    if "VpcPeeringConnectionId" in route:
        route_target_type = RouteTargetType.VPC_PEERING
        route_target_id = route["VpcPeeringConnectionId"]
    elif "GatewayId" in route and route["GatewayId"].startswith("igw-"):
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
    tags = convert_list_to_dict(route_table.get("Tags"), "Key", "Value")
    return RouteTable(route_table_id, routes, vpc_id, tags)


def map_ec2ippermission_to_firewallrule(ip_permission: Dict[str, Any]) -> FirewallRule:
    ip_protocol = ip_permission["IpProtocol"]
    from_port = ip_permission.get("FromPort", -1)
    to_port = ip_permission.get("ToPort", -1)
    ip_range = ip_permission["IpRanges"][0]
    cidr = ip_range["CidrIp"]
    return FirewallRule(from_port, to_port, ip_protocol, cidr)


def map_ec2securitygroup_to_firewallruleset(
    security_group: Dict[str, Any]
) -> FirewallRuleset:
    id = security_group["GroupId"]
    vpc_id = security_group["VpcId"]
    tags = convert_list_to_dict(security_group.get("Tags"), "Key", "Value")
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
    tags = convert_list_to_dict(vpc_peering.get("Tags"), "Key", "Value")
    return VpcPeering(id, status, role, requester_vpc_id, accepter_vpc_id, tags)


def map_ecstaskdefinition_to_containerdefinition(
    task_definition: Dict[str, Any],
    tag_list: List[Dict[str, str]],
) -> ContainerDefinition:
    task_definition_arn = task_definition["taskDefinitionArn"]
    container_definition = task_definition["containerDefinitions"][0]
    container_name = container_definition["name"]
    task_definition_id = get_container_definition_id(
        task_definition_arn, container_name
    )
    image = container_definition["image"]
    cpu = container_definition.get("cpu", task_definition.get("cpu"))
    memory = container_definition.get("memory", task_definition.get("memory"))
    entry_point = container_definition.get("entryPoint", [])
    environment = convert_list_to_dict(
        container_definition["environment"], "name", "value"
    )
    task_role_id = task_definition.get("taskRoleArn", None)
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


def map_awsstatement_to_policystatement(statement: Dict[str, Any]) -> PolicyStatement:
    # resource is optional for s3 policy
    resources = (
        convert_obj_to_list(statement["Resource"]) if "Resource" in statement else []
    )
    return PolicyStatement(
        effect=statement["Effect"],
        principals=get_json_values(statement["Principal"]),
        actions=convert_obj_to_list(statement["Action"]),
        resources=resources,
    )
