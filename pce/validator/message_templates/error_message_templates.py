#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

# patternlint-disable f-string-may-be-missing-leading-f

from enum import Enum

from pce.validator.message_templates.pce_standard_constants import (
    CONTAINER_CPU,
    CONTAINER_IMAGE,
    CONTAINER_MEMORY,
    FIREWALL_RULE_FINAL_PORT,
    FIREWALL_RULE_INITIAL_PORT,
    IGW_ROUTE_DESTINATION_CIDR_BLOCK,
)

# PCE networking validation error messages
class NetworkingErrorTemplate(Enum):
    # VPC
    VPC_NON_PRIVATE_CIDR = "The CIDR of the vpc {vpc_cidr} is not a private range."

    # Firewall
    FIREWALL_CIDR_NOT_OVERLAPS_VPC = "VPC peering for VPC {peer_target_id} doesn't have an inbound rule to allow traffic to {vpc_id}:{vpc_cidr}."
    FIREWALL_CIDR_CANT_CONTAIN_EXPECTED_RANGE = f"Ingress cidr {{fr_vpc_id}}:{{fri_cidr}}:{{fri_from_port}}-{{fri_to_port}} does not contain all required ports from {FIREWALL_RULE_INITIAL_PORT} to {FIREWALL_RULE_FINAL_PORT}"
    FIREWALL_INVALID_RULESETS = "Invalid firewall rulesets: {error_reasons}."
    FIREWALL_PEER_ROUTE_NOT_SET = "No peer route found."
    FIREWALL_RULES_NOT_FOUND = "No firewall rules found tagged with {pce_id}."

    # Subnets
    SUBNETS_NOT_ALL_AZ_USED = "Subnets are not using all availability zones from {region}, currently using {azs}."

    # Route table
    ROUTE_TABLE_IGW_MISSING = "Internet Gateway route missing in route table."
    ROUTE_TABLE_IGW_INACTIVE = "Internet Gateway route is not Active."
    ROUTE_TABLE_VPC_PEERING_MISSING = (
        "No Active route for VPC Peering Connection found in the route table."
    )

    # VPC peering
    VPC_PEERING_NO_VPC_PEERING = "No VPC peering set."
    VPC_PEERING_NO_VPC = "VPC not found."
    VPC_PEERING_NO_VPC_CIDR = "No VPC CIDR set."
    VPC_PEERING_NO_ROUTE_TABLE = "No route table set."
    # Unacceptable states include VpcPeeringState.REJECTED and VpcPeeringState.NOT_READY
    # The latter maps any other state not explicitly listed in the VpcPeeringState Enum
    VPC_PEERING_UNACCEPTABLE_STATE = "VPC Peering is in unacceptable state: {status}."

    # Network unknown error
    NETWORKING_UNKNOWN = "PCE Networking unknown error"


# PCE Compute validation error messages
class ComputeErrorTemplate(Enum):
    # Container cluster
    CLUSTER_DEFINITION_NOT_SET = "No container definition."
    CLUSTER_DEFINITION_WRONG_VALUES = (
        "Container values incorrectly set: {error_reasons}"
    )
    CLUSTER_DEFINITION_WRONG_VALUE = (
        "{resource_name} value '{value}' is incorrect, expected '{expected_value}'."
    )
    ROLE_WRONG_POLICY = "None of the policies ({policy_names}) attached to the role {role_name} conform to standard."
    ROLE_POLICIES_NOT_FOUND = "Policies not attached to {role_names}."

    # Compute unknown error
    UNKNOWN = "PCE Compute Unknown error"


# PCE Networking solution hint
class NetworkingErrorSolutionHintTemplate(Enum):
    # VPC
    ROUTE_TABLE_VPC_PEERING_MISSING = (
        "Ensure that a route for VPC Peering Connection is present and Active in the route table. "
        "If present but not Active, check if the VPC Peering Connection request is pending "
        "acceptance by the owner of the Acceptor VPC."
    )

    # Firewall
    FIREWALL_CIDR_CANT_CONTAIN_EXPECTED_RANGE = (
        "Update the port range for {sec_group} to {from_port}-{to_port}."
    )
    FIREWALL_INVALID_RULESETS = "To remediate: {error_remediation}"

    # Subnets
    SUBNETS_NOT_ALL_AZ_USED = (
        "Set the subnets so that all availability zones are used, {azs} are missing."
    )

    # Route table
    ROUTE_TABLE_IGW_MISSING = (
        f"Ensure that a route for destination {IGW_ROUTE_DESTINATION_CIDR_BLOCK} "
        "to an Internet Gateway target is added to the route table."
    )
    ROUTE_TABLE_IGW_INACTIVE = (
        "Ensure that the Internet Gateway route in the routing table is in the Active state. "
        "Recreate the Internet Gateway resource if needed or reach out to AWS Support for troubleshooting."
    )
    # VPC Peering
    VPC_NON_PRIVATE_CIDR = "Set a private CIDR {default_vpc_cidr} for the vpc."


class ComputeErrorSolutionHintTemplate(Enum):
    # Compute Cluster
    CLUSTER_DEFINITION_WRONG_VALUES = f"Please set container values (cpu, memory, image) as ({CONTAINER_CPU},{CONTAINER_MEMORY},'{CONTAINER_IMAGE}')"
    ROLE_WRONG_POLICY = "Set the policy of {role_name} to {role_policy}."
    ROLE_POLICIES_NOT_FOUND = (
        "Make sure there are policies attached to {role_names} in the pce {pce_id}."
    )
