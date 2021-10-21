#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import ipaddress
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List, Tuple

from fbpcp.entity.firewall_ruleset import FirewallRuleset
from fbpcp.entity.pce import PCE
from fbpcp.entity.route_table import Route, RouteState, RouteTargetType
from fbpcp.entity.vpc_instance import Vpc
from fbpcp.entity.vpc_peering import VpcPeeringState
from pce.gateway.ec2 import EC2Gateway
from pce.validator.message_templates import (
    ValidationErrorDescriptionTemplate,
    ValidationErrorSolutionHintTemplate,
    ValidationWarningDescriptionTemplate,
    ValidationWarningSolutionHintTemplate,
)
from pce.validator.pce_standard_constants import (
    FIREWALL_RULE_INITIAL_PORT,
    FIREWALL_RULE_FINAL_PORT,
    CONTAINER_CPU,
    CONTAINER_MEMORY,
    CONTAINER_IMAGE,
)


class ValidationResultCode(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass
class ValidationResult:
    validation_result_code: ValidationResultCode = ValidationResultCode.ERROR
    description: Optional[str] = None
    solution_hint: Optional[str] = None


class ClusterResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    IMAGE = "image"


class ValidationSuite:
    def __init__(
        self,
        region: str,
        key_id: str,
        key_data: str,
        config: Optional[Dict[str, Any]] = None,
        ec2_gateway: Optional[EC2Gateway] = None,
    ) -> None:
        self.ec2_gateway: EC2Gateway = ec2_gateway or EC2Gateway(
            region, key_id, key_data, config
        )

    def validate_private_cidr(self, pce: PCE) -> ValidationResult:
        vpc = pce.pce_network.vpc
        if not vpc:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.VPC_PEERING_NO_VPC.value,
            )
        is_valid = ipaddress.ip_network(vpc.cidr).is_private
        return (
            ValidationResult(ValidationResultCode.SUCCESS)
            if is_valid
            else ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.NON_PRIVATE_VPC_CIDR.value.format(
                    vpc_cidr=vpc.vpc_id
                ),
                ValidationErrorSolutionHintTemplate.NON_PRIVATE_VPC_CIDR.value,
            )
        )

    def validate_vpc_peering(self, pce: PCE) -> ValidationResult:
        vpc_peering = pce.pce_network.vpc_peering
        if not vpc_peering:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.VPC_PEERING_NO_VPC_PEERING.value,
            )

        state_results = defaultdict(
            lambda: ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.UNKNOWN.value,
            ),
            {
                VpcPeeringState.ACTIVE: ValidationResult(ValidationResultCode.SUCCESS),
                VpcPeeringState.PENDING_ACCEPTANCE: ValidationResult(
                    ValidationResultCode.WARNING,
                    ValidationWarningDescriptionTemplate.VPC_PEERING_PEERING_NOT_READY.value,
                    ValidationWarningSolutionHintTemplate.VPC_PEERING_PEERING_NOT_READY.value,
                ),
            },
        )

        return state_results[vpc_peering.status]

    def _check_inbound_peer_route_allowed(
        self,
        peer_routes: List[Route],
        firewall_rulesets: List[FirewallRuleset],
        vpc: Vpc,
    ) -> Tuple[List[str], List[str]]:
        """
        For each peer route check if there is an inbound rule for it. If there is, make sure the port range of the rule is within PCE standard range. The results are returned in 2 lists of messages, one for errors and one for warnings.
        """
        error_reasons = []
        warning_reasons = []

        for peer_route in peer_routes:
            peer_cidr = peer_route.destination_cidr_block
            peer_rule_found = False
            for fr in firewall_rulesets:
                for fri in fr.ingress:
                    if not ipaddress.ip_network(fri.cidr).overlaps(
                        ipaddress.ip_network(peer_cidr)
                    ):
                        continue
                    peer_rule_found = True
                    if (
                        FIREWALL_RULE_INITIAL_PORT < fri.from_port
                        or FIREWALL_RULE_FINAL_PORT > fri.to_port
                    ):
                        error_reasons.append(
                            ValidationErrorDescriptionTemplate.FIREWALL_CIDR_CANT_CONTAIN_EXPECTED_RANGE.value.format(
                                fr_vpc_id=fr.vpc_id,
                                fri_cidr=fri.cidr,
                                fri_from_port=fri.from_port,
                                fri_to_port=fri.to_port,
                            ),
                        )
                    elif (
                        FIREWALL_RULE_INITIAL_PORT > fri.from_port
                        or FIREWALL_RULE_FINAL_PORT < fri.to_port
                    ):
                        warning_reasons.append(
                            ValidationWarningDescriptionTemplate.FIREWALL_CIDR_EXCEED_EXPECTED_RANGE.value.format(
                                fr_vpc_id=fr.vpc_id,
                                fri_cidr=fri.cidr,
                                fri_from_port=fri.from_port,
                                fri_to_port=fri.to_port,
                            )
                        )
            if not peer_rule_found:
                error_reasons.append(
                    ValidationErrorDescriptionTemplate.FIREWALL_CIDR_NOT_OVERLAPS_VPC.value.format(
                        peer_target_id=peer_route.route_target.route_target_id,
                        vpc_id=vpc.vpc_id,
                        vpc_cidr=vpc.cidr,
                    )
                )

        return error_reasons, warning_reasons

    def validate_firewall(self, pce: PCE) -> ValidationResult:
        """
        Check that among inbound traffic from the peers is allowed i.e. there is a rule whose CIDR is overlapped by any firewall rule.
        """
        vpc = pce.pce_network.vpc
        if not vpc:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.VPC_PEERING_NO_VPC.value,
            )
        vpc_cidr = vpc.cidr
        if not vpc_cidr:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.VPC_PEERING_NO_VPC_CIDR.value,
            )
        # Don't bother in validating route table if there are no firewall rules
        firewall_rulesets = pce.pce_network.firewall_rulesets
        if not firewall_rulesets:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.FIREWALL_RULES_NOT_FOUND.value.format(
                    pce_id=vpc.tags["pce:pce-id"]
                ),
            )
        route_table = pce.pce_network.route_table
        if not route_table:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.VPC_PEERING_NO_ROUTE_TABLE.value,
            )
        peer_routes = [
            r
            for r in (route_table.routes if route_table else [])
            if r.route_target.route_target_type == RouteTargetType.VPC_PEERING
        ]
        if not peer_routes:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.FIREWALL_PEER_ROUTE_NOT_SET.value,
            )

        error_reasons, warning_reasons = self._check_inbound_peer_route_allowed(
            peer_routes, firewall_rulesets, vpc
        )

        if error_reasons:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.FIREWALL_INVALID_RULESETS.value.format(
                    error_reasons=";".join(error_reasons)
                ),
                ValidationErrorSolutionHintTemplate.FIREWALL_INVALID_RULESETS.value,
            )
        if warning_reasons:
            return ValidationResult(
                ValidationResultCode.WARNING,
                ValidationWarningDescriptionTemplate.FIREWALL_FLAGGED_RULESETS.value.format(
                    warning_reasons=";".join(warning_reasons)
                ),
            )

        return ValidationResult(ValidationResultCode.SUCCESS)

    def validate_route_table(self, pce: PCE) -> ValidationResult:
        """
        Make sure there is a an entry in the route table for the VPC peer and that it is active
        """
        vpc = pce.pce_network.vpc
        if not vpc:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.VPC_PEERING_NO_VPC.value,
            )
        route_table = pce.pce_network.route_table
        if not route_table:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.VPC_PEERING_NO_ROUTE_TABLE.value,
            )

        is_valid = any(
            r.state == RouteState.ACTIVE
            and r.route_target.route_target_type == RouteTargetType.VPC_PEERING
            for r in (route_table.routes if route_table else [])
        )

        return (
            ValidationResult(ValidationResultCode.SUCCESS)
            if is_valid
            else ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.ROUTE_TABLE_VPC_PEERING_MISSING.value,
                ValidationErrorSolutionHintTemplate.ROUTE_TABLE_VPC_PEERING_MISSING.value,
            )
        )

    # Check that all subnets make use of every AZ in the VPC region
    def validate_subnets(self, pce: PCE) -> ValidationResult:
        region_azs = self.ec2_gateway.describe_availability_zones()
        is_valid = len(set(region_azs)) == len(
            {s.availability_zone for s in pce.pce_network.subnets}
        )
        return (
            ValidationResult(ValidationResultCode.SUCCESS)
            if is_valid
            else ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.NOT_ALL_AZ_USED.value,
                ValidationErrorSolutionHintTemplate.NOT_ALL_AZ_USED.value.format(
                    region=pce.pce_network.region, azs=",".join(region_azs)
                ),
            )
        )

    # Check CPU, memory and image name values are according to the standard
    def validate_cluster_definition(self, pce: PCE) -> ValidationResult:
        c = pce.pce_compute.container_definition
        if not c:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.CLUSTER_DEFINITION_NOT_SET.value,
            )
        message_by_level = defaultdict(list)
        for resource, expected_value, level in (
            (
                ClusterResourceType.CPU,
                CONTAINER_CPU,
                ValidationResultCode.ERROR,
            ),
            (
                ClusterResourceType.MEMORY,
                CONTAINER_MEMORY,
                ValidationResultCode.ERROR,
            ),
            (
                ClusterResourceType.IMAGE,
                CONTAINER_IMAGE,
                ValidationResultCode.WARNING,
            ),
        ):
            value = getattr(c, resource.value)
            if value != expected_value:
                message_template = (
                    ValidationErrorDescriptionTemplate.CLUSTER_DEFINITION_WRONG_VALUE.value
                    if ValidationResultCode.ERROR == level
                    else ValidationWarningDescriptionTemplate.CLUSTER_DEFINITION_FLAGGED_VALUE.value
                )
                message = message_template.format(
                    resource_name=resource.value.title(),
                    value=value,
                    expected_value=expected_value,
                )
                message_by_level[level].append(message)

        if message_by_level[ValidationResultCode.ERROR]:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.CLUSTER_DEFINITION_WRONG_VALUES.value.format(
                    error_reasons=",".join(message_by_level[ValidationResultCode.ERROR])
                ),
                ValidationErrorSolutionHintTemplate.CLUSTER_DEFINITION_WRONG_VALUES.value,
            )
        elif message_by_level[ValidationResultCode.WARNING]:
            return ValidationResult(
                ValidationResultCode.WARNING,
                ValidationWarningDescriptionTemplate.CLUSTER_DEFINITION_FLAGGED_VALUES.value.format(
                    warning_reasons=",".join(
                        message_by_level[ValidationResultCode.WARNING]
                    )
                ),
            )
        return ValidationResult(ValidationResultCode.SUCCESS)

    def validate_network_and_compute(self, pce: PCE) -> List[ValidationResult]:
        """
        Execute all existing validations returning warnings and errors encapsulated in `ValidationResult` objects
        """
        return [
            vr
            for vr in [
                validation_function(pce)
                for validation_function in [
                    self.validate_private_cidr,
                    self.validate_vpc_peering,
                    self.validate_firewall,
                    self.validate_route_table,
                    self.validate_subnets,
                    self.validate_cluster_definition,
                ]
            ]
            if ValidationResultCode.SUCCESS != vr.validation_result_code
        ]

    @classmethod
    def summarize_errors(cls, validation_results: List[ValidationResult]) -> str:
        results_by_code = defaultdict(list)
        for result in validation_results:
            results_by_code[result.validation_result_code].append(result)
        return "\n".join(
            [
                f"{code}:\n\t"
                + "\n\t".join(
                    [
                        f"{res.description}{f' {res.solution_hint}' if res.solution_hint else ''}"
                        for res in results
                    ]
                )
                for code, results in results_by_code.items()
            ]
        )
