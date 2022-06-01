#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import ipaddress
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple

import click
from fbpcp.entity.firewall_ruleset import FirewallRuleset
from fbpcp.entity.pce import PCE
from fbpcp.entity.route_table import Route, RouteState, RouteTargetType
from fbpcp.entity.vpc_instance import Vpc
from fbpcp.entity.vpc_peering import VpcPeeringState
from fbpcp.service.pce_aws import PCE_ID_KEY
from pce.entity.mpc_roles import MPCRoles
from pce.gateway.ec2 import EC2Gateway
from pce.gateway.ecs import ECSGateway
from pce.gateway.iam import IAMGateway
from pce.gateway.logs_aws import LogsGateway
from pce.validator.message_templates.error_message_templates import (
    ComputeErrorSolutionHintTemplate,
    ComputeErrorTemplate,
    NetworkingErrorSolutionHintTemplate,
    NetworkingErrorTemplate,
)
from pce.validator.message_templates.pce_standard_constants import (
    CONTAINER_CPU,
    CONTAINER_IMAGE,
    CONTAINER_MEMORY,
    DEFAULT_PARTNER_VPC_CIDR,
    DEFAULT_VPC_CIDR,
    FIREWALL_RULE_FINAL_PORT,
    FIREWALL_RULE_INITIAL_PORT,
    IGW_ROUTE_DESTINATION_CIDR_BLOCK,
    TASK_POLICY,
)
from pce.validator.message_templates.validator_step_names import ValidationStepNames
from pce.validator.message_templates.warning_message_templates import (
    NetworkingValidationWarningDescriptionTemplate,
    ValidationWarningDescriptionTemplate,
    ValidationWarningSolutionHintTemplate,
)


class ValidationResultCode(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass
class ValidationResult:
    validation_result_code: ValidationResultCode = ValidationResultCode.ERROR
    validation_step_name: Optional[str] = None
    description: Optional[str] = None
    solution_hint: Optional[str] = None

    def __str__(self) -> str:
        return f"ValidationStepName.{self.validation_step_name}: {self.description}{f' {self.solution_hint}' if self.solution_hint else ''}"

    def __hash__(self) -> int:
        return hash(self.__str__())


class ClusterResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    IMAGE = "image"


class ValidationSuite:
    def __init__(
        self,
        region: str,
        key_id: Optional[str] = None,
        key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        role: Optional[MPCRoles] = None,
        ec2_gateway: Optional[EC2Gateway] = None,
        iam_gateway: Optional[IAMGateway] = None,
        ecs_gateway: Optional[ECSGateway] = None,
        logs_gateway: Optional[LogsGateway] = None,
    ) -> None:
        self.role: MPCRoles = role or MPCRoles.PARTNER
        self.ec2_gateway: EC2Gateway = ec2_gateway or EC2Gateway(
            region, key_id, key_data, config
        )
        self.iam_gateway: IAMGateway = iam_gateway or IAMGateway(
            region, key_id, key_data, config
        )
        self.ecs_gateway: ECSGateway = ecs_gateway or ECSGateway(
            region, key_id, key_data, config
        )

        self.logs_gateway: LogsGateway = logs_gateway or LogsGateway(
            region, key_id, key_data, config
        )

    def validate_vpc_cidr(self, pce: PCE) -> ValidationResult:
        default_vpc_cidr = (
            DEFAULT_PARTNER_VPC_CIDR
            if self.role == MPCRoles.PARTNER
            else DEFAULT_VPC_CIDR
        )
        vpc = pce.pce_network.vpc
        if not vpc:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.VPC_CIDR.code_name,
                NetworkingErrorTemplate.VPC_PEERING_NO_VPC.value,
            )
        vpc_network = ipaddress.ip_network(vpc.cidr)
        valid_network = ipaddress.ip_network(default_vpc_cidr)
        is_valid = (
            vpc_network.is_private
            and (vpc_network[0] in valid_network)
            and (vpc_network[-1] in valid_network)
        )

        return (
            ValidationResult(
                ValidationResultCode.SUCCESS, ValidationStepNames.VPC_CIDR.code_name
            )
            if is_valid
            else ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.VPC_CIDR.code_name,
                NetworkingErrorTemplate.VPC_NON_PRIVATE_CIDR.value.format(
                    vpc_cidr=vpc.vpc_id
                ),
                NetworkingErrorSolutionHintTemplate.VPC_NON_PRIVATE_CIDR.value.format(
                    default_vpc_cidr=DEFAULT_PARTNER_VPC_CIDR
                ),
            )
        )

    def validate_vpc_peering(self, pce: PCE) -> ValidationResult:
        if self.role == MPCRoles.PARTNER:
            vpc_peering = pce.pce_network.vpc_peering
        else:
            vpc = pce.pce_network.vpc
            vpc_peering = (
                self.ec2_gateway.describe_vpc_peering_connections_with_accepter_vpc_id(
                    vpc_id=vpc.vpc_id
                )
                if vpc
                else None
            )

        if not vpc_peering:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.VPC_PEERING.code_name,
                NetworkingErrorTemplate.VPC_PEERING_NO_VPC_PEERING.value,
            )

        state_results = defaultdict(
            lambda: ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.VPC_PEERING.code_name,
                NetworkingErrorTemplate.VPC_PEERING_UNACCEPTABLE_STATE.value.format(
                    status=vpc_peering.status
                ),
            ),
            {
                VpcPeeringState.ACTIVE: ValidationResult(
                    ValidationResultCode.SUCCESS,
                    ValidationStepNames.VPC_PEERING.code_name,
                ),
                VpcPeeringState.PENDING_ACCEPTANCE: ValidationResult(
                    ValidationResultCode.WARNING,
                    ValidationStepNames.VPC_PEERING.code_name,
                    NetworkingValidationWarningDescriptionTemplate.NETWORKING_VPC_PEERING_PEERING_NOT_READY.value,
                    ValidationWarningSolutionHintTemplate.VPC_PEERING_PEERING_NOT_READY.value.format(
                        accepter_vpc_id=vpc_peering.accepter_vpc_id
                    ),
                ),
            },
        )

        return state_results[vpc_peering.status]

    def _check_inbound_peer_route_allowed(
        self,
        peer_routes: List[Route],
        firewall_rulesets: List[FirewallRuleset],
        vpc: Vpc,
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        For each peer route check if there is an inbound rule for it. If there is, make sure the port range of the rule is within PCE standard range. The results are returned in 2 lists of messages, one for errors and one for warnings.
        """
        error_reasons = []
        error_remediation = []
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
                            NetworkingErrorTemplate.FIREWALL_CIDR_CANT_CONTAIN_EXPECTED_RANGE.value.format(
                                fr_vpc_id=fr.vpc_id,
                                fri_cidr=fri.cidr,
                                fri_from_port=fri.from_port,
                                fri_to_port=fri.to_port,
                            ),
                        )
                        error_remediation.append(
                            NetworkingErrorSolutionHintTemplate.FIREWALL_CIDR_CANT_CONTAIN_EXPECTED_RANGE.value.format(
                                sec_group=fr.id,
                                from_port=FIREWALL_RULE_INITIAL_PORT,
                                to_port=FIREWALL_RULE_FINAL_PORT,
                            ),
                        )
                    elif (
                        FIREWALL_RULE_INITIAL_PORT > fri.from_port
                        or FIREWALL_RULE_FINAL_PORT < fri.to_port
                    ):
                        warning_reasons.append(
                            NetworkingValidationWarningDescriptionTemplate.NETWORKING_FIREWALL_CIDR_EXCEED_EXPECTED_RANGE.value.format(
                                fr_vpc_id=fr.vpc_id,
                                fri_cidr=fri.cidr,
                                fri_from_port=fri.from_port,
                                fri_to_port=fri.to_port,
                            )
                        )
            if not peer_rule_found:
                error_reasons.append(
                    NetworkingErrorTemplate.FIREWALL_CIDR_NOT_OVERLAPS_VPC.value.format(
                        peer_target_id=peer_route.route_target.route_target_id,
                        vpc_id=vpc.vpc_id,
                        vpc_cidr=vpc.cidr,
                    )
                )

        return error_reasons, error_remediation, warning_reasons

    def validate_firewall(self, pce: PCE) -> ValidationResult:
        """
        Check that inbound traffic from the peers is allowed i.e. there is a rule whose CIDR is overlapped by any firewall rule.
        """
        vpc = pce.pce_network.vpc
        if not vpc:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.FIREWALL.code_name,
                NetworkingErrorTemplate.VPC_PEERING_NO_VPC.value,
            )
        vpc_cidr = vpc.cidr
        if not vpc_cidr:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.FIREWALL.code_name,
                NetworkingErrorTemplate.VPC_PEERING_NO_VPC_CIDR.value,
            )
        # Don't bother in validating route table if there are no firewall rules
        firewall_rulesets = pce.pce_network.firewall_rulesets
        if not firewall_rulesets:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.FIREWALL.code_name,
                NetworkingErrorTemplate.FIREWALL_RULES_NOT_FOUND.value.format(
                    pce_id=vpc.tags[PCE_ID_KEY]
                ),
            )
        route_table = pce.pce_network.route_table
        if not route_table:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.FIREWALL.code_name,
                NetworkingErrorTemplate.VPC_PEERING_NO_ROUTE_TABLE.value,
            )
        peer_routes = [
            r
            for r in (route_table.routes if route_table else [])
            if r.route_target.route_target_type == RouteTargetType.VPC_PEERING
        ]
        if not peer_routes:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.FIREWALL.code_name,
                NetworkingErrorTemplate.FIREWALL_PEER_ROUTE_NOT_SET.value,
            )

        (
            error_reasons,
            error_remediation,
            warning_reasons,
        ) = self._check_inbound_peer_route_allowed(peer_routes, firewall_rulesets, vpc)

        if error_reasons:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.FIREWALL.code_name,
                NetworkingErrorTemplate.FIREWALL_INVALID_RULESETS.value.format(
                    error_reasons=";".join(error_reasons)
                ),
                NetworkingErrorSolutionHintTemplate.FIREWALL_INVALID_RULESETS.value.format(
                    error_remediation=";".join(error_remediation)
                ),
            )
        if warning_reasons:
            return ValidationResult(
                ValidationResultCode.WARNING,
                ValidationStepNames.FIREWALL.code_name,
                NetworkingValidationWarningDescriptionTemplate.NETWORKING_FIREWALL_FLAGGED_RULESETS.value.format(
                    warning_reasons=";".join(warning_reasons)
                ),
            )

        return ValidationResult(
            ValidationResultCode.SUCCESS, ValidationStepNames.FIREWALL.code_name
        )

    def validate_route_table(self, pce: PCE) -> ValidationResult:
        """
        Make sure routing table has all the required routes in active state
        This includes routes for a Peering Connection and an Internet Gateway
        """
        vpc = pce.pce_network.vpc
        if not vpc:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.ROUTE_TABLE.code_name,
                NetworkingErrorTemplate.VPC_PEERING_NO_VPC.value,
            )
        route_table = pce.pce_network.route_table
        if not route_table:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.ROUTE_TABLE.code_name,
                NetworkingErrorTemplate.VPC_PEERING_NO_ROUTE_TABLE.value,
            )

        is_vpc_peering_valid = any(
            r.state == RouteState.ACTIVE
            and r.route_target.route_target_type == RouteTargetType.VPC_PEERING
            for r in (route_table.routes if route_table else [])
        )

        if not is_vpc_peering_valid:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.ROUTE_TABLE.code_name,
                NetworkingErrorTemplate.ROUTE_TABLE_VPC_PEERING_MISSING.value,
                NetworkingErrorSolutionHintTemplate.ROUTE_TABLE_VPC_PEERING_MISSING.value,
            )

        igw_route = None
        for route in route_table.routes:
            if (
                route.route_target.route_target_type == RouteTargetType.INTERNET
                and route.destination_cidr_block == IGW_ROUTE_DESTINATION_CIDR_BLOCK
            ):
                igw_route = route

        if not igw_route:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.ROUTE_TABLE.code_name,
                NetworkingErrorTemplate.ROUTE_TABLE_IGW_MISSING.value,
                NetworkingErrorSolutionHintTemplate.ROUTE_TABLE_IGW_MISSING.value,
            )

        if igw_route.state != RouteState.ACTIVE:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.ROUTE_TABLE.code_name,
                NetworkingErrorTemplate.ROUTE_TABLE_IGW_INACTIVE.value,
                NetworkingErrorSolutionHintTemplate.ROUTE_TABLE_IGW_INACTIVE.value,
            )

        return ValidationResult(
            ValidationResultCode.SUCCESS, ValidationStepNames.ROUTE_TABLE.code_name
        )

    def validate_subnets(self, pce: PCE) -> ValidationResult:
        """
        Check that all subnets make use of every AZ in the VPC region
        """
        region_azs = set(self.ec2_gateway.describe_availability_zones())
        used_azs = {s.availability_zone for s in pce.pce_network.subnets}
        # There can't be a case where AZs are used and are not among the region AZs
        is_valid = region_azs == used_azs
        return (
            ValidationResult(
                ValidationResultCode.SUCCESS, ValidationStepNames.SUBNETS.code_name
            )
            if is_valid
            else ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.SUBNETS.code_name,
                NetworkingErrorTemplate.SUBNETS_NOT_ALL_AZ_USED.value.format(
                    region=pce.pce_network.region,
                    azs=",".join(sorted(used_azs)) if used_azs else "none",
                ),
                NetworkingErrorSolutionHintTemplate.SUBNETS_NOT_ALL_AZ_USED.value.format(
                    azs=",".join(sorted(region_azs - used_azs)),
                ),
            )
        )

    def validate_cluster_definition(self, pce: PCE) -> ValidationResult:
        """
        Check CPU, memory and image name values are according to the standard
        """
        c = pce.pce_compute.container_definition
        if not c:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.CLUSTER_DEFINITION.code_name,
                ComputeErrorTemplate.CLUSTER_DEFINITION_NOT_SET.value,
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
                    ComputeErrorTemplate.CLUSTER_DEFINITION_WRONG_VALUE.value
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
                ValidationStepNames.CLUSTER_DEFINITION.code_name,
                ComputeErrorTemplate.CLUSTER_DEFINITION_WRONG_VALUES.value.format(
                    error_reasons=",".join(message_by_level[ValidationResultCode.ERROR])
                ),
                ComputeErrorSolutionHintTemplate.CLUSTER_DEFINITION_WRONG_VALUES.value,
            )
        elif message_by_level[ValidationResultCode.WARNING]:
            return ValidationResult(
                ValidationResultCode.WARNING,
                ValidationStepNames.CLUSTER_DEFINITION.code_name,
                ValidationWarningDescriptionTemplate.CLUSTER_DEFINITION_FLAGGED_VALUES.value.format(
                    warning_reasons=",".join(
                        message_by_level[ValidationResultCode.WARNING]
                    )
                ),
            )
        return ValidationResult(
            ValidationResultCode.SUCCESS,
            ValidationStepNames.CLUSTER_DEFINITION.code_name,
        )

    def validate_network_and_compute(
        self, pce: PCE, skip_steps: Optional[List[ValidationStepNames]] = None
    ) -> List[ValidationResult]:
        """
        Execute all existing validations returning warnings and errors encapsulated in `ValidationResult` objects
        """
        validation_steps: Iterable[ValidationStepNames] = list(ValidationStepNames)
        if skip_steps:
            validation_steps = filter(
                lambda step: step not in skip_steps, validation_steps
            )
        with click.progressbar(
            [
                (
                    self.__getattribute__(f"validate_{step.code_name}"),
                    step.formatted_name,
                )
                for step in validation_steps
            ],
            item_show_func=lambda i: str(i[1]) if i else "",
            label="Validating PCE...",
        ) as validation_functions:
            return [
                vr
                for vr in [
                    validation_function(pce)
                    for validation_function, _ in validation_functions
                ]
                if ValidationResultCode.SUCCESS != vr.validation_result_code
            ]

    @classmethod
    def summarize_errors(cls, validation_results: List[ValidationResult]) -> str:
        results_by_code = defaultdict(list)
        for result in validation_results:
            results_by_code[result.validation_result_code].append(result)
        summary = ""
        for code, results in results_by_code.items():
            for result in results:
                summary += f"{code}: {result}\n"
        return summary

    @classmethod
    def contains_error_result(cls, results: List[ValidationResult]) -> bool:
        return any(
            [
                result
                for result in results
                if result.validation_result_code == ValidationResultCode.ERROR
            ]
        )

    def validate_iam_roles(self, pce: PCE) -> ValidationResult:
        """
        Ensure that the container task execution role has the proper policy (`TASK_POLICY`) among those attached to it.
        """
        c = pce.pce_compute.container_definition
        if not c:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.IAM_ROLES.code_name,
                ComputeErrorTemplate.CLUSTER_DEFINITION_NOT_SET.value,
            )

        policies = self.iam_gateway.get_policies_for_role(c.task_role_id)

        if not policies:
            pce_id = c.tags[PCE_ID_KEY]
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.IAM_ROLES.code_name,
                ComputeErrorTemplate.ROLE_POLICIES_NOT_FOUND.value.format(
                    role_names=c.task_role_id
                ),
                ComputeErrorSolutionHintTemplate.ROLE_POLICIES_NOT_FOUND.value.format(
                    role_names=c.task_role_id, pce_id=pce_id
                ),
            )

        policy_name_found = None
        for policy_name, policy_contents in policies.attached_policy_contents.items():
            if TASK_POLICY == policy_contents:
                policy_name_found = policy_name
                break

        if not policy_name_found:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.IAM_ROLES.code_name,
                ComputeErrorTemplate.ROLE_WRONG_POLICY.value.format(
                    role_name=c.task_role_id,
                    policy_names=",".join(policies.attached_policy_contents.keys()),
                ),
                ComputeErrorSolutionHintTemplate.ROLE_WRONG_POLICY.value.format(
                    role_name=c.task_role_id,
                    role_policy=TASK_POLICY,
                ),
            )

        if len(policies.attached_policy_contents.values()) > 1:
            return ValidationResult(
                ValidationResultCode.WARNING,
                ValidationStepNames.IAM_ROLES.code_name,
                ValidationWarningDescriptionTemplate.MORE_POLICIES_THAN_EXPECTED.value.format(
                    policy_names=",".join(
                        policies.attached_policy_contents.keys() - {policy_name_found}
                    ),
                    role_id=c.task_role_id,
                ),
                ValidationWarningSolutionHintTemplate.MORE_POLICIES_THAN_EXPECTED.value,
            )
        return ValidationResult(
            ValidationResultCode.SUCCESS, ValidationStepNames.IAM_ROLES.code_name
        )

    def validate_log_group(self, pce: PCE) -> ValidationResult:
        c = pce.pce_compute.container_definition
        if not c:
            return ValidationResult(
                ValidationResultCode.ERROR,
                ValidationStepNames.LOG_GROUP.code_name,
                ComputeErrorTemplate.CLUSTER_DEFINITION_NOT_SET.value,
            )

        log_group_name_from_task = self.ecs_gateway.extract_log_group_name(c.id)
        if not log_group_name_from_task:
            return ValidationResult(
                ValidationResultCode.WARNING,
                ValidationStepNames.LOG_GROUP.code_name,
                ValidationWarningDescriptionTemplate.CLOUDWATCH_LOGS_NOT_CONFIGURED_IN_TASK_DEFINITION.value,
            )

        log_group = self.logs_gateway.describe_log_group(
            log_group_name=log_group_name_from_task
        )

        if log_group and log_group.log_group_name:
            return ValidationResult(
                ValidationResultCode.SUCCESS, ValidationStepNames.LOG_GROUP.code_name
            )

        return ValidationResult(
            ValidationResultCode.WARNING,
            ValidationStepNames.LOG_GROUP.code_name,
            ValidationWarningDescriptionTemplate.CLOUDWATCH_LOGS_NOT_FOUND.value.format(
                log_group_name_from_task=log_group_name_from_task
            ),
        )
