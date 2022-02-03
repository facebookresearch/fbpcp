#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

# patternlint-disable f-string-may-be-missing-leading-f

from enum import Enum

from pce.validator.pce_standard_constants import (
    FIREWALL_RULE_FINAL_PORT,
    FIREWALL_RULE_INITIAL_PORT,
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
