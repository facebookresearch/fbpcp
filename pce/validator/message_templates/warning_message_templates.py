#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

# patternlint-disable f-string-may-be-missing-leading-f

from enum import Enum

from pce.validator.message_templates.pce_standard_constants import (
    FIREWALL_RULE_FINAL_PORT,
    FIREWALL_RULE_INITIAL_PORT,
)

# for scenarios should raise up warning messages are
# 1) the current PCE setup is not a blocker for running study, however not fully follow the PCE set up standard.
# 2) run time components are still in pending status


class NetworkingValidationWarningDescriptionTemplate(Enum):
    NETWORKING_VPC_PEERING_PEERING_NOT_READY = (
        "VPC Peering Connection request is pending acceptance."
    )
    NETWORKING_FIREWALL_CIDR_EXCEED_EXPECTED_RANGE = f"Ingress cidr {{fr_vpc_id}}:{{fri_cidr}}:{{fri_from_port}}-{{fri_to_port}} exceeds the expected port range {FIREWALL_RULE_INITIAL_PORT}-{FIREWALL_RULE_FINAL_PORT}"
    NETWORKING_FIREWALL_FLAGGED_RULESETS = (
        "These issues are not fatal but are worth noticing: {warning_reasons}"
    )


class ValidationWarningDescriptionTemplate(Enum):
    CLUSTER_DEFINITION_FLAGGED_VALUE = (
        "{resource_name} value '{value}' is not expected, should be '{expected_value}'."
    )
    CLUSTER_DEFINITION_FLAGGED_VALUES = (
        "Container has outlier values which are non-fatal: {warning_reasons}"
    )
    MORE_POLICIES_THAN_EXPECTED = (
        "Policies {policy_names} attached to {role_id} are not expected."
    )
    CLOUDWATCH_LOGS_NOT_CONFIGURED_IN_TASK_DEFINITION = (
        "CloudWatch logs are not configured in ECS task definition."
    )
    CLOUDWATCH_LOGS_NOT_FOUND = "CloudWatch logs are not found, please check if log group name {log_group_name_from_task} is correct or if this log group gets deleted "


class ValidationWarningSolutionHintTemplate(Enum):
    VPC_PEERING_PEERING_NOT_READY = "Please work with owner of Acceptor VPC (VPC ID: {accepter_vpc_id}) to accept peering request."
    MORE_POLICIES_THAN_EXPECTED = (
        "Consider removing additional policies to strengthen security."
    )
