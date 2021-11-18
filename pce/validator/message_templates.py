#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

# patternlint-disable f-string-may-be-missing-leading-f

from enum import Enum

from pce.validator.pce_standard_constants import (
    FIREWALL_RULE_INITIAL_PORT,
    FIREWALL_RULE_FINAL_PORT,
    CONTAINER_CPU,
    CONTAINER_MEMORY,
    CONTAINER_IMAGE,
)


class ValidationErrorDescriptionTemplate(Enum):
    UNKNOWN = "Unknown error"
    VPC_PEERING_NO_VPC_PEERING = "No VPC peering set."
    VPC_PEERING_NO_VPC = "VPC not found."
    VPC_PEERING_NO_VPC_CIDR = "No VPC CIDR set."
    VPC_PEERING_NO_ROUTE_TABLE = "No route table set."
    # @lint-ignore This is a valid/inteneded usage of a string as a template
    FIREWALL_CIDR_NOT_OVERLAPS_VPC = "VPC peering for VPC {peer_target_id} doesn't have an inbound rule to allow traffic to {vpc_id}:{vpc_cidr}."
    FIREWALL_CIDR_CANT_CONTAIN_EXPECTED_RANGE = f"Ingress cidr {{fr_vpc_id}}:{{fri_cidr}}:{{fri_from_port}}-{{fri_to_port}} can't contain the expected port range {FIREWALL_RULE_INITIAL_PORT}-{FIREWALL_RULE_FINAL_PORT}"
    FIREWALL_INVALID_RULESETS = "Invalid firewall rulesets: {error_reasons}"
    ROUTE_TABLE_VPC_PEERING_MISSING = "No valid VPC peering found in route table."
    CLUSTER_DEFINITION_NOT_SET = "No container definition."
    CLUSTER_DEFINITION_WRONG_VALUES = (
        "Container values incorrectly set: {error_reasons}"
    )
    NON_PRIVATE_VPC_CIDR = "The CIDR of the vpc {vpc_cidr} is not a private range."
    NOT_ALL_AZ_USED = "Subnets are not using all availability zones from {region}, currently using {azs}."
    FIREWALL_PEER_ROUTE_NOT_SET = "No peer route found."
    FIREWALL_RULES_NOT_FOUND = "No firewall rules found tagged with {pce_id}."
    CLUSTER_DEFINITION_WRONG_VALUE = (
        "{resource_name} value '{value}' is incorrect, expected '{expected_value}'."
    )
    ROLE_WRONG_POLICY = "None of the policies ({policy_names}) attached to the role {role_name} conform to standard."
    ROLE_POLICIES_NOT_FOUND = "Policies not attached to {role_names}."


class ValidationErrorSolutionHintTemplate(Enum):
    FIREWALL_INVALID_RULESETS = (
        "Set correct CIDR and port ranges for the offending firewall rules."
    )
    ROUTE_TABLE_VPC_PEERING_MISSING = "Define a VPC connection in the route table."
    CLUSTER_DEFINITION_WRONG_VALUES = f"Please set container values (cpu, memory, image) as ({CONTAINER_CPU},{CONTAINER_MEMORY},'{CONTAINER_IMAGE}')"
    NON_PRIVATE_VPC_CIDR = "Set a private CIDR (https://en.wikipedia.org/wiki/Private_network) for the vpc."
    NOT_ALL_AZ_USED = (
        "Set the subnets so that all availability zones are used, {azs} are missing."
    )
    ROLE_WRONG_POLICY = "Set the policy of {role_name} to {role_policy}."
    ROLE_POLICIES_NOT_FOUND = (
        "Make sure there are policies attached to {role_names} in the pce {pce_id}."
    )


class ValidationWarningDescriptionTemplate(Enum):
    VPC_PEERING_PEERING_NOT_READY = "Still setting up peering."
    FIREWALL_CIDR_EXCEED_EXPECTED_RANGE = f"Ingress cidr {{fr_vpc_id}}:{{fri_cidr}}:{{fri_from_port}}-{{fri_to_port}} exceeds the expected port range {FIREWALL_RULE_INITIAL_PORT}-{FIREWALL_RULE_FINAL_PORT}"
    FIREWALL_FLAGGED_RULESETS = (
        "These issues are not fatal but are worth noticing: {warning_reasons}"
    )
    CLUSTER_DEFINITION_FLAGGED_VALUE = (
        "{resource_name} value '{value}' is not expected, should be '{expected_value}'."
    )
    CLUSTER_DEFINITION_FLAGGED_VALUES = (
        "Container has outlier values which are non-fatal: {warning_reasons}"
    )
    MORE_POLICIES_THAN_EXPECTED = (
        "Policies {policy_names} attached to {role_id} are not expected."
    )


class ValidationWarningSolutionHintTemplate(Enum):
    VPC_PEERING_PEERING_NOT_READY = "Please try again in a moment."
    MORE_POLICIES_THAN_EXPECTED = (
        "Consider removing additional policies to strengthen security."
    )


class ValidationStepNames(Enum):
    CIDR = "CIDR"
    VPC_PEERING = "VPC peering"
    FIREWALL = "Firewall"
    ROUTE_TABLE = "Route table"
    SUBNETS = "Subnets"
    CLUSTER_DEFINITION = "Cluster definition"
    ROLE = "IAM roles"
