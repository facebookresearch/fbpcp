#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from decimal import Decimal

from fbpcp.entity.cloud_cost import CloudCost, CloudCostItem
from fbpcp.entity.cluster_instance import ClusterStatus, Cluster
from fbpcp.entity.container_instance import ContainerInstanceStatus, ContainerInstance
from fbpcp.entity.route_table import (
    Route,
    RouteState,
    RouteTarget,
    RouteTargetType,
)
from fbpcp.entity.subnet import Subnet
from fbpcp.mapper.aws import (
    map_ecstask_to_containerinstance,
    map_esccluster_to_clusterinstance,
    map_ec2subnet_to_subnet,
    map_cecost_to_cloud_cost,
    map_ec2route_to_route,
)


class TestAWSMapper(unittest.TestCase):
    TEST_IP_ADDRESS = "127.0.0.1"
    TEST_TASK_ARN = "test-task-arn"
    TEST_CLUSTER_ARN = "test-cluster-arn"
    TEST_CLUSTER_NAME = "test-cluster-name"
    TEST_LOCAL_ROUTE_CIDR = "10.0.0.0/16"
    TEST_LOCAL_TARGET_ID = "local"
    TEST_IGW_ROUTE_CIDR = "0.0.0.0/0"
    TEST_IGW_TARGET_ID = "igw-a1b2c3d000"
    TEST_ROUTE_STATE_ACTIVE = "active"
    TEST_ROUTE_STATE_INACTIVE = "blackhole"

    def test_map_ecstask_to_containerinstance(self):
        ecs_task_response = {
            "tasks": [
                {
                    "containers": [
                        {
                            "exitCode": None,
                            "lastStatus": "RUNNING",
                            "networkInterfaces": [
                                {
                                    "privateIpv4Address": self.TEST_IP_ADDRESS,
                                },
                            ],
                        },
                    ],
                    "taskArn": self.TEST_TASK_ARN,
                },
                {
                    "containers": [
                        {
                            "exitCode": 0,
                            "lastStatus": "STOPPED",
                            "networkInterfaces": [],
                        },
                    ],
                    "taskArn": self.TEST_TASK_ARN,
                },
                {
                    "containers": [
                        {
                            "exitCode": 1,
                            "lastStatus": "STOPPED",
                            "networkInterfaces": [],
                        },
                    ],
                    "taskArn": self.TEST_TASK_ARN,
                },
                {
                    "containers": [
                        {
                            "exitCode": -1,
                            "lastStatus": "UNKNOWN",
                            "networkInterfaces": [],
                        },
                    ],
                    "taskArn": self.TEST_TASK_ARN,
                },
            ]
        }

        expected_task_list = [
            ContainerInstance(
                self.TEST_TASK_ARN,
                self.TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
            ContainerInstance(
                self.TEST_TASK_ARN,
                None,
                ContainerInstanceStatus.COMPLETED,
            ),
            ContainerInstance(
                self.TEST_TASK_ARN,
                None,
                ContainerInstanceStatus.FAILED,
            ),
            ContainerInstance(
                self.TEST_TASK_ARN,
                None,
                ContainerInstanceStatus.UNKNOWN,
            ),
        ]
        tasks_list = [
            map_ecstask_to_containerinstance(task)
            for task in ecs_task_response["tasks"]
        ]

        self.assertEqual(tasks_list, expected_task_list)

    def test_map_esccluster_to_clusterinstance(self):
        tag_key_1 = "tag-key-1"
        tag_key_2 = "tag-key-2"
        tag_value_1 = "tag-value-1"
        tag_value_2 = "tag-value-2"
        running_tasks = 100
        pending_tasks = 1
        ecs_cluster_response = {
            "clusters": [
                {
                    "clusterName": self.TEST_CLUSTER_NAME,
                    "clusterArn": self.TEST_CLUSTER_ARN,
                    "status": "ACTIVE",
                    "runningTasksCount": running_tasks,
                    "pendingTasksCount": pending_tasks,
                    "tags": [
                        {
                            "key": tag_key_1,
                            "value": tag_value_1,
                        },
                        {
                            "key": tag_key_2,
                            "value": tag_value_2,
                        },
                    ],
                },
                {
                    "clusterName": self.TEST_CLUSTER_NAME,
                    "clusterArn": self.TEST_CLUSTER_ARN,
                    "status": "INACTIVE",
                    "runningTasksCount": running_tasks,
                    "pendingTasksCount": pending_tasks,
                    "tags": [
                        {
                            "key": tag_key_1,
                            "value": tag_value_1,
                        },
                    ],
                },
                {
                    "clusterName": self.TEST_CLUSTER_NAME,
                    "clusterArn": self.TEST_CLUSTER_ARN,
                    "status": "UNKNOWN",
                    "runningTasksCount": running_tasks,
                    "pendingTasksCount": pending_tasks,
                    "tags": [
                        {
                            "key": tag_key_1,
                            "value": tag_value_1,
                        },
                    ],
                },
            ]
        }
        multi_tag_value_pair = {
            tag_key_1: tag_value_1,
            tag_key_2: tag_value_2,
        }
        single_tag_value_pair = {tag_key_1: tag_value_1}

        expected_cluster_list = [
            Cluster(
                self.TEST_CLUSTER_ARN,
                self.TEST_CLUSTER_NAME,
                pending_tasks,
                running_tasks,
                ClusterStatus.ACTIVE,
                multi_tag_value_pair,
            ),
            Cluster(
                self.TEST_CLUSTER_ARN,
                self.TEST_CLUSTER_NAME,
                pending_tasks,
                running_tasks,
                ClusterStatus.INACTIVE,
                single_tag_value_pair,
            ),
            Cluster(
                self.TEST_CLUSTER_ARN,
                self.TEST_CLUSTER_NAME,
                pending_tasks,
                running_tasks,
                ClusterStatus.UNKNOWN,
                single_tag_value_pair,
            ),
        ]
        cluster_list = [
            map_esccluster_to_clusterinstance(cluster)
            for cluster in ecs_cluster_response["clusters"]
        ]

        self.assertEqual(cluster_list, expected_cluster_list)

    def test_map_es2subnet_to_subnet(self):
        test_subnet_id = "subnet-a0b1c3d4e5"
        test_az = "us-west-2a"
        test_tag_key = "Name"
        test_tag_value = "test_value"
        ec2_client_response = {
            "AvailabilityZone": test_az,
            "SubnetId": test_subnet_id,
            "Tags": [{"Key": test_tag_key, "Value": test_tag_value}],
        }
        expected_subnet = Subnet(
            test_subnet_id, test_az, {test_tag_key: test_tag_value}
        )

        self.assertEqual(map_ec2subnet_to_subnet(ec2_client_response), expected_subnet)

    def test_map_cecost_to_cloud_cost(self):
        test_service = "Amazon Macie"
        test_amount_1 = "0.0049312"
        test_amount_2 = "0.051"
        test_amount_expected = Decimal(test_amount_1) + Decimal(test_amount_2)
        ce_client_response = [
            {
                "TimePeriod": {"Start": "2021-08-01", "End": "2021-08-02"},
                "Groups": [
                    {
                        "Keys": [test_service],
                        "Metrics": {
                            "UnblendedCost": {"Amount": test_amount_1, "Unit": "USD"}
                        },
                    },
                ],
            },
            {
                "TimePeriod": {"Start": "2021-08-02", "End": "2021-08-03"},
                "Groups": [
                    {
                        "Keys": [test_service],
                        "Metrics": {
                            "UnblendedCost": {"Amount": test_amount_2, "Unit": "USD"}
                        },
                    },
                ],
            },
        ]
        expected_cloud_cost = CloudCost(
            total_cost_amount=test_amount_expected,
            details=[
                CloudCostItem(
                    service=test_service,
                    cost_amount=test_amount_expected,
                )
            ],
        )
        self.assertEqual(
            map_cecost_to_cloud_cost(ce_client_response),
            expected_cloud_cost,
        )

    def test_map_ec2route_to_route_parse_local(self):
        local_route_response = {
            "DestinationCidrBlock": self.TEST_LOCAL_ROUTE_CIDR,
            "GatewayId": self.TEST_LOCAL_TARGET_ID,
            "State": self.TEST_ROUTE_STATE_ACTIVE,
        }
        expected_parsed_route = Route(
            self.TEST_LOCAL_ROUTE_CIDR,
            RouteTarget(route_target_type=RouteTargetType.OTHER, route_target_id=""),
            RouteState.ACTIVE,
        )
        self.assertEqual(
            map_ec2route_to_route(local_route_response), expected_parsed_route
        )

    def test_map_ec2route_to_route_parse_internet_gateway(self):
        igw_route_response = {
            "DestinationCidrBlock": self.TEST_IGW_ROUTE_CIDR,
            "GatewayId": self.TEST_IGW_TARGET_ID,
            "State": self.TEST_ROUTE_STATE_ACTIVE,
        }
        expected_parsed_route = Route(
            self.TEST_IGW_ROUTE_CIDR,
            RouteTarget(
                route_target_type=RouteTargetType.INTERNET,
                route_target_id=self.TEST_IGW_TARGET_ID,
            ),
            RouteState.ACTIVE,
        )
        self.assertEqual(
            map_ec2route_to_route(igw_route_response), expected_parsed_route
        )

    def test_map_ec2route_to_route_parse_internet_gateway_inactive(self):
        igw_route_response = {
            "DestinationCidrBlock": self.TEST_IGW_ROUTE_CIDR,
            "GatewayId": self.TEST_IGW_TARGET_ID,
            "State": self.TEST_ROUTE_STATE_INACTIVE,
        }
        expected_parsed_route = Route(
            self.TEST_IGW_ROUTE_CIDR,
            RouteTarget(
                route_target_type=RouteTargetType.INTERNET,
                route_target_id=self.TEST_IGW_TARGET_ID,
            ),
            RouteState.UNKNOWN,
        )
        self.assertEqual(
            map_ec2route_to_route(igw_route_response), expected_parsed_route
        )
