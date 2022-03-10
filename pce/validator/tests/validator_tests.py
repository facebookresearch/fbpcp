#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Optional, List, Dict, Any
from unittest import TestCase
from unittest.mock import MagicMock

from fbpcp.entity.container_definition import ContainerDefinition
from fbpcp.entity.firewall_ruleset import FirewallRuleset, FirewallRule
from fbpcp.entity.route_table import (
    RouteTargetType,
    Route,
    RouteState,
)
from fbpcp.entity.subnet import Subnet
from fbpcp.entity.vpc_peering import VpcPeeringState
from fbpcp.service.pce_aws import PCE_ID_KEY
from pce.entity.iam_role import (
    IAMRole,
    RoleId,
    PolicyContents,
)
from pce.entity.log_group_aws import LogGroup
from pce.entity.mpc_roles import MPCRoles
from pce.validator.message_templates.pce_standard_constants import (
    AvailabilityZone,
    CONTAINER_CPU,
    CONTAINER_IMAGE,
    CONTAINER_MEMORY,
    FIREWALL_RULE_FINAL_PORT,
    FIREWALL_RULE_INITIAL_PORT,
    IGW_ROUTE_DESTINATION_CIDR_BLOCK,
    IGW_ROUTE_TARGET_PREFIX,
    TASK_POLICY,
    DEFAULT_PARTNER_VPC_CIDR,
    DEFAULT_VPC_CIDR,
)
from pce.validator.validation_suite import (
    ValidationResult,
    ValidationResultCode,
    ValidationErrorDescriptionTemplate,
    ValidationErrorSolutionHintTemplate,
    NetworkingValidationWarningDescriptionTemplate,
    ValidationWarningDescriptionTemplate,
    ValidationWarningSolutionHintTemplate,
    ClusterResourceType,
    ValidationSuite,
)


def create_mock_firewall_rule(
    cidr: str,
    from_port: int = FIREWALL_RULE_INITIAL_PORT,
    to_port: int = FIREWALL_RULE_FINAL_PORT,
) -> FirewallRule:
    fr = MagicMock()
    fr.from_port = from_port
    fr.to_port = to_port
    fr.cidr = cidr
    return fr


def create_mock_firewall_rule_set(ingress: List[FirewallRule]) -> FirewallRuleset:
    frs = MagicMock()
    frs.vpc_id = "create_mock_firewall_rule_set"
    frs.ingress = ingress
    return frs


def create_mock_route(
    cidr: str,
    target_type: RouteTargetType,
    state: RouteState = RouteState.ACTIVE,
    route_target_id: str = "",
) -> Route:
    r = MagicMock()
    r.destination_cidr_block = cidr
    r.state = state
    r.route_target = MagicMock()
    r.route_target.route_target_type = target_type
    r.route_target.route_target_id = (
        f"target_{target_type.name}_{cidr}"
        if route_target_id == ""
        else route_target_id
    )
    return r


def create_mock_valid_igw_route(**kwargs: Any) -> Route:
    return create_mock_route(
        cidr=IGW_ROUTE_DESTINATION_CIDR_BLOCK,
        target_type=RouteTargetType.INTERNET,
        route_target_id=f"{IGW_ROUTE_TARGET_PREFIX}1a2b3c4d0000",
        **kwargs,
    )


def create_mock_subnet(availability_zone: AvailabilityZone) -> Subnet:
    s = MagicMock()
    s.availability_zone = availability_zone
    return s


def create_mock_container_definition(
    cpu: Optional[int] = None,
    memory: Optional[int] = None,
    image: Optional[str] = None,
    task_role_id: Optional[str] = None,
    execution_role_id: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
) -> ContainerDefinition:
    c = MagicMock()
    c.cpu = cpu
    c.memory = memory
    c.image = image
    c.task_role_id = task_role_id
    c.execution_role_id = execution_role_id
    c.tags = tags
    return c


def create_mock_log_group(
    log_group_name: Optional[str] = None,
) -> LogGroup:
    log_group = MagicMock()
    log_group.log_group_name = log_group_name
    return log_group


class TestValidator(TestCase):
    TEST_REGION = "us-east-1"
    TEST_REGION_AZS = [
        "us-east-1-bos-1a",
        "us-east-1-chi-1a",
        "us-east-1-dfw-1a",
    ]
    TEST_VPC_ID = "test_vpc_id"
    TEST_PCE_ID = "test_pce_id"
    TEST_ACCOUNT_ID = 123456789
    TEST_TASK_ROLE_NOT_RELATED_NAME = "test_task_role_bad_name"
    TEST_TASK_ROLE_NAME = "test_task_role_name"
    TEST_TASK_ROLE_ID = f"foo::bar::role/{TEST_TASK_ROLE_NAME}"
    TEST_TASK_ROLE_NOT_RELATED_ID = f"foo::bar::role/{TEST_TASK_ROLE_NOT_RELATED_NAME}"
    TEST_POLICY_TASK_ROLE_NAME = "a/b/test_policy_task_role_name"
    TEST_LOG_GROUP_NAME = "/ecs/test_log_group"
    TEST_NONEXIST_LOG_GROUP_NAME = "/etc/nonexist_log_group"

    def setUp(self) -> None:
        self.ec2_gateway = MagicMock()
        self.iam_gateway = MagicMock()
        self.logs_gateway = MagicMock()
        self.ecs_gateway = MagicMock()
        self.validator = ValidationSuite(
            "test_region",
            "test_key_id",
            "test_key_data",
            ec2_gateway=self.ec2_gateway,
            iam_gateway=self.iam_gateway,
            ecs_gateway=self.ecs_gateway,
            logs_gateway=self.logs_gateway,
        )
        self.maxDiff = None

    def _test_validate_private_cidr(
        self,
        cidr: str,
        expected_result: Optional[ValidationResult],
        expected_error_msg: Optional[str] = None,
    ) -> None:
        pce = MagicMock()
        pce.pce_network = MagicMock()
        pce.pce_network.vpc = MagicMock()
        pce.pce_network.vpc.vpc_id = TestValidator.TEST_VPC_ID
        pce.pce_network.region = "us-east-1"
        pce.pce_network.vpc.cidr = cidr

        if expected_error_msg:
            with self.assertRaises(Exception) as ex:
                self.validator.validate_private_cidr(pce)
            self.assertEquals(expected_error_msg, str(ex.exception))
            return

        actual_result = self.validator.validate_private_cidr(pce)
        self.assertEquals(expected_result, actual_result)

    def test_validate_private_cidr_non_valid(self) -> None:
        for invalid_ip in ["non_valid", "10.1.1.300"]:
            self._test_validate_private_cidr(
                invalid_ip,
                None,
                f"'{invalid_ip}' does not appear to be an IPv4 or IPv6 network",
            )

    def test_validate_private_cidr_success(self) -> None:
        for invalid_ip in ["10.1.0.0/16", "10.1.10.0/24", "10.1.128.128/28"]:
            self._test_validate_private_cidr(
                invalid_ip, ValidationResult(ValidationResultCode.SUCCESS)
            )

    def test_validate_private_cidr_fail(self) -> None:
        for invalid_ip in ["10.0.0.0/7", "173.16.0.0/12", "192.168.0.0/15"]:
            self._test_validate_private_cidr(
                invalid_ip,
                ValidationResult(
                    ValidationResultCode.ERROR,
                    ValidationErrorDescriptionTemplate.NON_PRIVATE_VPC_CIDR.value.format(
                        vpc_cidr=TestValidator.TEST_VPC_ID
                    ),
                    ValidationErrorSolutionHintTemplate.NON_PRIVATE_VPC_CIDR.value.format(
                        default_vpc_cidr=DEFAULT_PARTNER_VPC_CIDR
                    ),
                ),
                None,
            )

    def test_validate_partner_cidr(self) -> None:
        pce = MagicMock()
        pce.pce_network.vpc.cidr = DEFAULT_PARTNER_VPC_CIDR
        self.validator.role = MPCRoles.PARTNER
        expected_result = ValidationResult(ValidationResultCode.SUCCESS)
        actual_result = self.validator.validate_private_cidr(pce)
        self.assertEquals(expected_result, actual_result)

    def test_validate_publisher_cidr(self) -> None:
        pce = MagicMock()
        pce.pce_network.vpc.cidr = DEFAULT_VPC_CIDR
        self.validator.role = MPCRoles.PUBLISHER
        expected_result = ValidationResult(ValidationResultCode.SUCCESS)
        actual_result = self.validator.validate_private_cidr(pce)
        self.assertEquals(expected_result, actual_result)

    def _test_validate_firewall(
        self,
        vpc_cidr: str,
        routes: List[Route],
        firewall_rulesets: List[FirewallRuleset],
        expected_result: ValidationResult,
        expected_error_msg: Optional[str] = None,
    ) -> None:
        pce = MagicMock()
        pce.pce_network = MagicMock()
        pce.pce_network.vpc = MagicMock()
        pce.pce_network.vpc.vpc_id = TestValidator.TEST_VPC_ID
        pce.pce_network.vpc.cidr = vpc_cidr
        pce.pce_network.vpc.tags = {PCE_ID_KEY: TestValidator.TEST_PCE_ID}
        pce.pce_network.firewall_rulesets = firewall_rulesets
        pce.pce_network.route_table = MagicMock()
        pce.pce_network.route_table.routes = routes

        if expected_error_msg:
            with self.assertRaises(Exception) as ex:
                self.validator.validate_firewall(pce)
            self.assertEquals(expected_error_msg, str(ex.exception))
            return

        actual_result = self.validator.validate_firewall(pce)
        self.assertEquals(expected_result, actual_result)

    def test_validate_firewall_not_overlapping_vpc(self) -> None:
        """
        No firewall rules allows inbound traffic from the peer
        """
        self._test_validate_firewall(
            "10.1.0.0/16",
            [
                create_mock_route("11.2.0.0/16", RouteTargetType.VPC_PEERING),
            ],
            [
                create_mock_firewall_rule_set(
                    [
                        create_mock_firewall_rule("10.2.0.0/16"),
                        create_mock_firewall_rule("10.1.1.0/24"),
                        create_mock_firewall_rule("10.3.0.0/16"),
                    ]
                )
            ],
            ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.FIREWALL_INVALID_RULESETS.value.format(
                    error_reasons=str(
                        ValidationErrorDescriptionTemplate.FIREWALL_CIDR_NOT_OVERLAPS_VPC.value.format(
                            peer_target_id="target_VPC_PEERING_11.2.0.0/16",
                            vpc_id=TestValidator.TEST_VPC_ID,
                            vpc_cidr="10.1.0.0/16",
                        )
                    )
                ),
                ValidationErrorSolutionHintTemplate.FIREWALL_INVALID_RULESETS.value,
            ),
        )

    def test_validate_firewall_bad_port_range(self) -> None:
        initial_port = FIREWALL_RULE_INITIAL_PORT + 1
        self._test_validate_firewall(
            "10.1.0.0/16",
            [
                create_mock_route("12.4.1.0/24", RouteTargetType.VPC_PEERING),
            ],
            [
                create_mock_firewall_rule_set(
                    [
                        create_mock_firewall_rule("10.2.0.0/16"),
                        create_mock_firewall_rule("12.4.0.0/16", initial_port),
                        create_mock_firewall_rule("10.3.0.0/16"),
                    ]
                )
            ],
            ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.FIREWALL_INVALID_RULESETS.value.format(
                    error_reasons=str(
                        ValidationErrorDescriptionTemplate.FIREWALL_CIDR_CANT_CONTAIN_EXPECTED_RANGE.value.format(
                            fr_vpc_id="create_mock_firewall_rule_set",
                            fri_cidr="12.4.0.0/16",
                            fri_from_port=initial_port,
                            fri_to_port=FIREWALL_RULE_FINAL_PORT,
                        )
                    )
                ),
                ValidationErrorSolutionHintTemplate.FIREWALL_INVALID_RULESETS.value,
            ),
        )

    def test_validate_firewall_success(self) -> None:
        self._test_validate_firewall(
            "10.1.0.0/16",
            [
                create_mock_route("12.4.1.0/24", RouteTargetType.VPC_PEERING),
            ],
            [
                create_mock_firewall_rule_set(
                    [
                        create_mock_firewall_rule("10.2.0.0/16"),
                        create_mock_firewall_rule("12.4.0.0/16"),
                        create_mock_firewall_rule("10.3.0.0/16"),
                    ]
                )
            ],
            ValidationResult(ValidationResultCode.SUCCESS),
        )

    def test_validate_firewall_exceeding_port_range(self) -> None:
        initial_port = FIREWALL_RULE_INITIAL_PORT - 1
        self._test_validate_firewall(
            "10.1.0.0/16",
            [
                create_mock_route("12.4.1.0/24", RouteTargetType.VPC_PEERING),
            ],
            [
                create_mock_firewall_rule_set(
                    [
                        create_mock_firewall_rule("10.2.0.0/16"),
                        create_mock_firewall_rule("12.4.0.0/16", initial_port),
                        create_mock_firewall_rule("10.3.0.0/16"),
                    ]
                )
            ],
            ValidationResult(
                ValidationResultCode.WARNING,
                NetworkingValidationWarningDescriptionTemplate.NETWORKING_FIREWALL_FLAGGED_RULESETS.value.format(
                    warning_reasons=str(
                        NetworkingValidationWarningDescriptionTemplate.NETWORKING_FIREWALL_CIDR_EXCEED_EXPECTED_RANGE.value.format(
                            fr_vpc_id="create_mock_firewall_rule_set",
                            fri_cidr="12.4.0.0/16",
                            fri_from_port=initial_port,
                            fri_to_port=FIREWALL_RULE_FINAL_PORT,
                        )
                    )
                ),
            ),
        )

    def test_validate_firewall_no_rulez(self) -> None:
        self._test_validate_firewall(
            "10.1.0.0/16",
            [
                create_mock_route("12.4.1.0/24", RouteTargetType.VPC_PEERING),
            ],
            [],
            ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.FIREWALL_RULES_NOT_FOUND.value.format(
                    pce_id=TestValidator.TEST_PCE_ID
                ),
            ),
        )

    def _test_validate_route_table(
        self,
        routes: List[Route],
        expected_result: ValidationResult,
        expected_error_msg: Optional[str] = None,
    ) -> None:
        pce = MagicMock()
        pce.pce_network = MagicMock()
        pce.pce_network.vpc = MagicMock()
        pce.pce_network.route_table = MagicMock()
        pce.pce_network.route_table.routes = routes

        if expected_error_msg:
            with self.assertRaises(Exception) as ex:
                self.validator.validate_route_table(pce)
            self.assertEquals(expected_error_msg, str(ex.exception))
            return

        actual_result = self.validator.validate_route_table(pce)
        self.assertEquals(expected_result, actual_result)

    def test_validate_route_table_no_vpc_peering(self) -> None:
        self._test_validate_route_table(
            [
                create_mock_route("11.2.0.0/16", RouteTargetType.INTERNET),
                create_mock_route("11.3.0.0/16", RouteTargetType.OTHER),
                create_mock_route("11.4.0.0/16", RouteTargetType.INTERNET),
            ],
            ValidationResult(
                validation_result_code=ValidationResultCode.ERROR,
                description=ValidationErrorDescriptionTemplate.ROUTE_TABLE_VPC_PEERING_MISSING.value,
                solution_hint=ValidationErrorSolutionHintTemplate.ROUTE_TABLE_VPC_PEERING_MISSING.value,
            ),
        )

    def test_validate_route_table_route_not_active(self) -> None:
        self._test_validate_route_table(
            [
                create_mock_route("11.2.0.0/16", RouteTargetType.INTERNET),
                create_mock_route(
                    "10.3.0.0/16", RouteTargetType.VPC_PEERING, RouteState.UNKNOWN
                ),
                create_mock_route("11.4.0.0/16", RouteTargetType.INTERNET),
            ],
            ValidationResult(
                validation_result_code=ValidationResultCode.ERROR,
                description=ValidationErrorDescriptionTemplate.ROUTE_TABLE_VPC_PEERING_MISSING.value,
                solution_hint=ValidationErrorSolutionHintTemplate.ROUTE_TABLE_VPC_PEERING_MISSING.value,
            ),
        )

    def test_validate_route_table_success(self) -> None:
        self._test_validate_route_table(
            [
                create_mock_route("11.2.0.0/16", RouteTargetType.INTERNET),
                create_mock_route("10.1.0.0/16", RouteTargetType.VPC_PEERING),
                create_mock_valid_igw_route(),
            ],
            ValidationResult(ValidationResultCode.SUCCESS),
        )

    def test_validate_route_table_no_igw(self) -> None:
        self._test_validate_route_table(
            [
                create_mock_route("11.2.0.0/16", RouteTargetType.OTHER),
                create_mock_route("10.1.0.0/16", RouteTargetType.VPC_PEERING),
                # route present but target is not an Internet Gateway
                create_mock_route(
                    "11.2.0.0/16",
                    RouteTargetType.INTERNET,
                    route_target_id="vgw-a1b2c3d4",
                ),
                # route present, target correct but destination CIDR is
                # not IGW_ROUTE_DESTINATION_CIDR_BLOCK
                create_mock_route(
                    "11.2.0.0/16",
                    RouteTargetType.INTERNET,
                    route_target_id=f"{IGW_ROUTE_TARGET_PREFIX}a1b2c3d4",
                ),
            ],
            ValidationResult(
                validation_result_code=ValidationResultCode.ERROR,
                description=ValidationErrorDescriptionTemplate.ROUTE_TABLE_IGW_MISSING.value,
                solution_hint=ValidationErrorSolutionHintTemplate.ROUTE_TABLE_IGW_MISSING.value,
            ),
        )

    def test_validate_route_table_igw_inactive(self) -> None:
        self._test_validate_route_table(
            [
                create_mock_route("11.2.0.0/16", RouteTargetType.OTHER),
                create_mock_route("10.1.0.0/16", RouteTargetType.VPC_PEERING),
                create_mock_valid_igw_route(state=RouteState.UNKNOWN),
            ],
            ValidationResult(
                validation_result_code=ValidationResultCode.ERROR,
                description=ValidationErrorDescriptionTemplate.ROUTE_TABLE_IGW_INACTIVE.value,
                solution_hint=ValidationErrorSolutionHintTemplate.ROUTE_TABLE_IGW_INACTIVE.value,
            ),
        )

    def _test_validate_subnet(
        self,
        subnet_availability_zones: List[AvailabilityZone],
        region_availability_zones: List[AvailabilityZone],
        expected_result: ValidationResult,
        expected_error_msg: Optional[str] = None,
    ) -> None:
        pce = MagicMock()
        pce.pce_network = MagicMock()
        pce.pce_network.region = "us-east-1"
        pce.pce_network.subnets = [
            create_mock_subnet(az) for az in subnet_availability_zones
        ]
        self.ec2_gateway.describe_availability_zones = MagicMock(
            return_value=region_availability_zones
        )

        if expected_error_msg:
            with self.assertRaises(Exception) as ex:
                self.validator.validate_subnets(pce)
            self.assertEquals(expected_error_msg, str(ex.exception))
            return

        actual_result = self.validator.validate_subnets(pce)
        self.assertEquals(expected_result, actual_result)

    def test_validate_subnet_single_zone(self) -> None:
        subnet_availability_zones = [
            "us-east-1-bos-1a",
            "us-east-1-bos-1a",
            "us-east-1-bos-1a",
        ]
        self._test_validate_subnet(
            subnet_availability_zones,
            TestValidator.TEST_REGION_AZS,
            ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.NOT_ALL_AZ_USED.value.format(
                    region=TestValidator.TEST_REGION,
                    azs=",".join(set(subnet_availability_zones)),
                ),
                ValidationErrorSolutionHintTemplate.NOT_ALL_AZ_USED.value.format(
                    azs=",".join(
                        sorted(
                            set(TestValidator.TEST_REGION_AZS)
                            - set(subnet_availability_zones)
                        )
                    ),
                ),
            ),
        )

    def test_validate_subnet_more_subnets_than_zone(self) -> None:
        subnet_availability_zones = [
            "us-east-1-bos-1a",
            "us-east-1-chi-1a",
            "us-east-1-chi-1a",
        ]
        self._test_validate_subnet(
            subnet_availability_zones,
            TestValidator.TEST_REGION_AZS,
            ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.NOT_ALL_AZ_USED.value.format(
                    region=TestValidator.TEST_REGION,
                    azs=",".join(sorted(set(subnet_availability_zones))),
                ),
                ValidationErrorSolutionHintTemplate.NOT_ALL_AZ_USED.value.format(
                    azs=",".join(
                        sorted(
                            set(TestValidator.TEST_REGION_AZS)
                            - set(subnet_availability_zones)
                        )
                    ),
                ),
            ),
        )

    def test_validate_subnet_success(self) -> None:
        self._test_validate_subnet(
            TestValidator.TEST_REGION_AZS,
            TestValidator.TEST_REGION_AZS,
            ValidationResult(ValidationResultCode.SUCCESS),
        )

    def _test_validate_cluster_definition(
        self,
        cpu: int,
        memory: int,
        image: str,
        expected_result: ValidationResult,
        expected_error_msg: Optional[str] = None,
    ) -> None:
        pce = MagicMock()
        pce.pce_compute = MagicMock()
        pce.pce_compute.container_definition = create_mock_container_definition(
            cpu, memory, image
        )

        if expected_error_msg:
            with self.assertRaises(Exception) as ex:
                self.validator.validate_cluster_definition(pce)
            self.assertEquals(expected_error_msg, str(ex.exception))
            return

        actual_result = self.validator.validate_cluster_definition(pce)
        self.assertEquals(expected_result, actual_result)

    def test_validate_cluster_definition_wrong_cpu(self) -> None:
        cpu = CONTAINER_CPU * 2
        self._test_validate_cluster_definition(
            cpu,
            CONTAINER_MEMORY,
            CONTAINER_IMAGE,
            ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.CLUSTER_DEFINITION_WRONG_VALUES.value.format(
                    error_reasons=",".join(
                        [
                            ValidationErrorDescriptionTemplate.CLUSTER_DEFINITION_WRONG_VALUE.value.format(
                                resource_name=ClusterResourceType.CPU.name.title(),
                                value=cpu,
                                expected_value=CONTAINER_CPU,
                            )
                        ]
                    )
                ),
                ValidationErrorSolutionHintTemplate.CLUSTER_DEFINITION_WRONG_VALUES.value,
            ),
        )

    def test_validate_cluster_definition_success(self) -> None:
        self._test_validate_cluster_definition(
            CONTAINER_CPU,
            CONTAINER_MEMORY,
            CONTAINER_IMAGE,
            ValidationResult(ValidationResultCode.SUCCESS),
        )

    def test_validate_cluster_definition_wrong_image(self) -> None:
        image = "foo_image"
        self._test_validate_cluster_definition(
            CONTAINER_CPU,
            CONTAINER_MEMORY,
            image,
            ValidationResult(
                ValidationResultCode.WARNING,
                ValidationWarningDescriptionTemplate.CLUSTER_DEFINITION_FLAGGED_VALUES.value.format(
                    warning_reasons=",".join(
                        [
                            ValidationWarningDescriptionTemplate.CLUSTER_DEFINITION_FLAGGED_VALUE.value.format(
                                resource_name=ClusterResourceType.IMAGE.name.title(),
                                value=image,
                                expected_value=CONTAINER_IMAGE,
                            )
                        ]
                    )
                ),
            ),
        )

    def _test_validate_network_and_compute(
        self,
        vpc_cidr: str,
        routes: List[Route],
        firewall_rulesets: List[FirewallRuleset],
        cpu: int,
        expected_result: List[ValidationResult],
        expected_error_msg: Optional[str] = None,
    ) -> None:
        pce = MagicMock()
        pce.pce_network = MagicMock()
        pce.pce_network.vpc = MagicMock()
        pce.pce_network.vpc.vpc_id = TestValidator.TEST_VPC_ID
        pce.pce_network.vpc.cidr = vpc_cidr
        pce.pce_network.firewall_rulesets = firewall_rulesets
        pce.pce_network.route_table = MagicMock()
        pce.pce_network.route_table.routes = routes
        pce.pce_network.subnets = []
        pce.pce_network.vpc_peering = MagicMock()
        pce.pce_network.vpc_peering.status = VpcPeeringState.ACTIVE
        pce.pce_compute = MagicMock()
        pce.pce_compute.container_definition = create_mock_container_definition(
            cpu,
            CONTAINER_MEMORY,
            CONTAINER_IMAGE,
            task_role_id=TestValidator.TEST_TASK_ROLE_ID,
            tags={PCE_ID_KEY: TestValidator.TEST_PCE_ID},
        )

        self.iam_gateway.get_policies_for_role = MagicMock(
            return_value=IAMRole(
                TestValidator.TEST_TASK_ROLE_ID,
                {
                    TestValidator.TEST_POLICY_TASK_ROLE_NAME: TASK_POLICY,
                },
            )
        )

        self.ec2_gateway.describe_availability_zones = MagicMock(return_value=[])

        if expected_error_msg:
            with self.assertRaises(Exception) as ex:
                self.validator.validate_network_and_compute(pce)
            self.assertEquals(expected_error_msg, str(ex.exception))
            return

        actual_result = self.validator.validate_network_and_compute(pce)
        self.assertEquals(expected_result, actual_result)

    def test_validate_network_and_compute_not_overlapping_firewall_cidr_and_wrong_cpu(
        self,
    ) -> None:
        cpu = CONTAINER_CPU + 1
        self._test_validate_network_and_compute(
            "10.1.0.0/16",
            [
                create_mock_route("12.4.1.0/24", RouteTargetType.VPC_PEERING),
                create_mock_valid_igw_route(),
            ],
            [
                create_mock_firewall_rule_set(
                    [
                        create_mock_firewall_rule("10.2.0.0/16"),
                        create_mock_firewall_rule("10.1.1.0/24"),
                        create_mock_firewall_rule("10.3.0.0/16"),
                    ]
                )
            ],
            cpu,
            [
                ValidationResult(
                    ValidationResultCode.ERROR,
                    ValidationErrorDescriptionTemplate.FIREWALL_INVALID_RULESETS.value.format(
                        error_reasons=str(
                            ValidationErrorDescriptionTemplate.FIREWALL_CIDR_NOT_OVERLAPS_VPC.value.format(
                                peer_target_id="target_VPC_PEERING_12.4.1.0/24",
                                vpc_id=TestValidator.TEST_VPC_ID,
                                vpc_cidr="10.1.0.0/16",
                            )
                        )
                    ),
                    ValidationErrorSolutionHintTemplate.FIREWALL_INVALID_RULESETS.value,
                ),
                ValidationResult(
                    ValidationResultCode.ERROR,
                    ValidationErrorDescriptionTemplate.CLUSTER_DEFINITION_WRONG_VALUES.value.format(
                        error_reasons=",".join(
                            [
                                ValidationErrorDescriptionTemplate.CLUSTER_DEFINITION_WRONG_VALUE.value.format(
                                    resource_name=ClusterResourceType.CPU.name.title(),
                                    value=cpu,
                                    expected_value=CONTAINER_CPU,
                                )
                            ]
                        )
                    ),
                    ValidationErrorSolutionHintTemplate.CLUSTER_DEFINITION_WRONG_VALUES.value,
                ),
            ],
        )

    def _test_validate_roles(
        self,
        task_role_id: RoleId,
        task_role_policy: IAMRole,
        expected_result: ValidationResult,
        expected_error_msg: Optional[str] = None,
    ) -> None:
        pce = MagicMock()
        pce.pce_compute = MagicMock()
        pce.pce_compute.container_definition = create_mock_container_definition(
            task_role_id=task_role_id,
            tags={PCE_ID_KEY: TestValidator.TEST_PCE_ID},
        )

        def get_policies(role_id: RoleId) -> Optional[IAMRole]:
            if task_role_policy.role_id == role_id:
                return task_role_policy
            return None

        self.iam_gateway.get_policies_for_role = MagicMock(side_effect=get_policies)

        if expected_error_msg:
            with self.assertRaises(Exception) as ex:
                self.validator.validate_roles(pce)
            self.assertEquals(expected_error_msg, str(ex.exception))
            return

        actual_result = self.validator.validate_roles(pce)
        self.assertEquals(expected_result, actual_result)

    def test_validate_roles_bad_task_policy(self) -> None:
        bad_task_policy: PolicyContents = TASK_POLICY.copy()
        bad_task_policy["Version"] = "2020-01-01"
        self._test_validate_roles(
            TestValidator.TEST_TASK_ROLE_ID,
            IAMRole(
                TestValidator.TEST_TASK_ROLE_ID,
                {
                    TestValidator.TEST_POLICY_TASK_ROLE_NAME: bad_task_policy,
                },
            ),
            ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.ROLE_WRONG_POLICY.value.format(
                    policy_names=TestValidator.TEST_POLICY_TASK_ROLE_NAME,
                    role_name=TestValidator.TEST_TASK_ROLE_ID,
                ),
                ValidationErrorSolutionHintTemplate.ROLE_WRONG_POLICY.value.format(
                    role_name=TestValidator.TEST_TASK_ROLE_ID,
                    role_policy=TASK_POLICY,
                ),
            ),
        )

    def test_validate_roles_no_attached_policies(self) -> None:
        task_policy: PolicyContents = TASK_POLICY.copy()
        self._test_validate_roles(
            TestValidator.TEST_TASK_ROLE_ID,
            IAMRole(
                # This role is not attached to the container
                TestValidator.TEST_TASK_ROLE_NOT_RELATED_ID,
                {TestValidator.TEST_POLICY_TASK_ROLE_NAME: task_policy},
            ),
            ValidationResult(
                ValidationResultCode.ERROR,
                ValidationErrorDescriptionTemplate.ROLE_POLICIES_NOT_FOUND.value.format(
                    role_names=",".join((TestValidator.TEST_TASK_ROLE_ID,))
                ),
                ValidationErrorSolutionHintTemplate.ROLE_POLICIES_NOT_FOUND.value.format(
                    role_names=",".join((TestValidator.TEST_TASK_ROLE_ID,)),
                    pce_id=TestValidator.TEST_PCE_ID,
                ),
            ),
        )

    def test_validate_roles_more_policies_than_expected(self) -> None:
        additional_policy_name = "task_policy_name_additional"
        task_policy: PolicyContents = TASK_POLICY.copy()
        self._test_validate_roles(
            TestValidator.TEST_TASK_ROLE_ID,
            IAMRole(
                TestValidator.TEST_TASK_ROLE_ID,
                {
                    TestValidator.TEST_POLICY_TASK_ROLE_NAME: task_policy,
                    additional_policy_name: {},
                },
            ),
            ValidationResult(
                ValidationResultCode.WARNING,
                ValidationWarningDescriptionTemplate.MORE_POLICIES_THAN_EXPECTED.value.format(
                    policy_names=additional_policy_name,
                    role_id=TestValidator.TEST_TASK_ROLE_ID,
                ),
                ValidationWarningSolutionHintTemplate.MORE_POLICIES_THAN_EXPECTED.value,
            ),
        )

    def test_validate_log_group_deleted(self) -> None:
        pce = MagicMock()
        self.ecs_gateway.extract_log_group_name = MagicMock(
            return_value=TestValidator.TEST_NONEXIST_LOG_GROUP_NAME
        )
        self.logs_gateway.describe_log_group = MagicMock(return_value=None)

        expected_result = ValidationResult(
            ValidationResultCode.WARNING,
            ValidationWarningDescriptionTemplate.CLOUDWATCH_LOGS_NOT_FOUND.value.format(
                log_group_name_from_task=TestValidator.TEST_NONEXIST_LOG_GROUP_NAME
            ),
        )
        actual_result = self.validator.validate_log_group(pce)
        self.assertEquals(expected_result, actual_result)

    def test_validate_log_group_success(self) -> None:
        pce = MagicMock()
        self.ecs_gateway.extract_log_group_name = MagicMock(
            return_value=TestValidator.TEST_LOG_GROUP_NAME
        )
        self.logs_gateway.describe_log_group = create_mock_log_group(
            log_group_name=TestValidator.TEST_LOG_GROUP_NAME
        )
        expected_result = ValidationResult(ValidationResultCode.SUCCESS)
        actual_result = self.validator.validate_log_group(pce)
        self.assertEquals(expected_result, actual_result)

    def test_validate_log_group_not_configuered_in_task(self) -> None:
        pce = MagicMock()
        self.ecs_gateway.extract_log_group_name = MagicMock(return_value=None)
        expected_result = ValidationResult(
            ValidationResultCode.WARNING,
            ValidationWarningDescriptionTemplate.CLOUDWATCH_LOGS_NOT_CONFIGURED_IN_TASK_DEFINITION.value,
        )

        actual_result = self.validator.validate_log_group(pce)
        self.assertEquals(expected_result, actual_result)


class TestValidationSuite(TestCase):
    def test_contains_error_result(self) -> None:
        results = [
            ValidationResult(ValidationResultCode.WARNING),
            ValidationResult(ValidationResultCode.ERROR),
        ]
        self.assertTrue(ValidationSuite.contains_error_result(results))

    def test_contains_error_result_warnings_only(self) -> None:
        results = [
            ValidationResult(ValidationResultCode.WARNING),
            ValidationResult(ValidationResultCode.WARNING),
        ]
        self.assertFalse(ValidationSuite.contains_error_result(results))
