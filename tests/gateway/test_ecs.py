#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.entity.cluster_instance import ClusterStatus, Cluster
from fbpcp.entity.container_definition import ContainerDefinition
from fbpcp.entity.container_instance import ContainerInstanceStatus, ContainerInstance
from fbpcp.gateway.ecs import ECSGateway
from fbpcp.util.aws import convert_list_to_dict, get_container_definition_id


class TestECSGateway(unittest.TestCase):
    TEST_TASK_ARN = "test-task-arn"
    TEST_TASK_ARN_2 = "test-task-arn-2"
    TEST_TASK_ARN_DNE = "test-task-arn-dne"

    TEST_TASK_DEFINITION = "test-task-definition"
    TEST_TASK_DEFINITION_ARN = "test-task-definition-arn"
    TEST_CONTAINER = "test-container"
    TEST_CLUSTER = "test-cluster"
    TEST_CMD = "test-cmd"
    TEST_SUBNETS = ["test-subnet"]
    TEST_ACCESS_KEY_ID = "test-access-key-id"
    TEST_ACCESS_KEY_DATA = "test-access-key-data"
    TEST_IP_ADDRESS = "127.0.0.1"
    TEST_FILE = "test-file"
    TEST_CLUSTER_TAG_KEY = "test-tag-key"
    TEST_CLUSTER_TAG_VALUE = "test-tag-value"
    REGION = "us-west-2"

    @patch("boto3.client")
    def setUp(self, BotoClient) -> None:
        self.gw = ECSGateway(
            self.REGION, self.TEST_ACCESS_KEY_ID, self.TEST_ACCESS_KEY_DATA
        )
        self.gw.client = BotoClient()

    def test_run_task(self) -> None:
        client_return_response = {
            "tasks": [
                {
                    "containers": [
                        {
                            "name": "container_1",
                            "exitcode": 123,
                            "lastStatus": "RUNNING",
                            "networkInterfaces": [
                                {
                                    "privateIpv4Address": self.TEST_IP_ADDRESS,
                                },
                            ],
                        }
                    ],
                    "taskArn": self.TEST_TASK_ARN,
                }
            ]
        }
        self.gw.client.run_task = MagicMock(return_value=client_return_response)
        task = self.gw.run_task(
            self.TEST_TASK_DEFINITION,
            self.TEST_CONTAINER,
            self.TEST_CMD,
            self.TEST_CLUSTER,
            self.TEST_SUBNETS,
        )
        expected_task = ContainerInstance(
            self.TEST_TASK_ARN,
            self.TEST_IP_ADDRESS,
            ContainerInstanceStatus.STARTED,
        )
        self.assertEqual(task, expected_task)
        self.gw.client.run_task.assert_called()

    def test_describe_task(self) -> None:
        client_return_response = {
            "tasks": [
                {
                    "containers": [
                        {
                            "name": self.TEST_CONTAINER,
                            "exitcode": 123,
                            "lastStatus": "RUNNING",
                            "networkInterfaces": [
                                {
                                    "privateIpv4Address": self.TEST_IP_ADDRESS,
                                },
                            ],
                        }
                    ],
                    "taskArn": self.TEST_TASK_ARN,
                }
            ],
            "failures": [],
        }
        self.gw.client.describe_tasks = MagicMock(return_value=client_return_response)
        container = self.gw.describe_task(self.TEST_CLUSTER, self.TEST_TASK_ARN)
        expected_container = ContainerInstance(
            self.TEST_TASK_ARN,
            self.TEST_IP_ADDRESS,
            ContainerInstanceStatus.STARTED,
        )

        self.assertEqual(container, expected_container)
        self.gw.client.describe_tasks.assert_called()

    def test_describe_task_nonexistent(self) -> None:
        client_return_response = {
            "tasks": [],
            "failures": [
                {"arn": self.TEST_TASK_ARN_DNE, "reason": "reason", "detail": "detail"},
            ],
        }
        self.gw.client.describe_tasks = MagicMock(return_value=client_return_response)
        container = self.gw.describe_task(self.TEST_CLUSTER, self.TEST_TASK_ARN_DNE)
        expected_container = None

        self.assertEqual(container, expected_container)
        self.gw.client.describe_tasks.assert_called()

    def test_describe_tasks(self) -> None:
        client_return_response = {
            "tasks": [
                {
                    "containers": [
                        {
                            "name": self.TEST_CONTAINER,
                            "exitcode": 123,
                            "lastStatus": "RUNNING",
                            "networkInterfaces": [
                                {
                                    "privateIpv4Address": self.TEST_IP_ADDRESS,
                                },
                            ],
                        }
                    ],
                    "taskArn": self.TEST_TASK_ARN,
                },
                {
                    "containers": [
                        {
                            "name": self.TEST_CONTAINER,
                            "exitcode": 123,
                            "lastStatus": "RUNNING",
                            "networkInterfaces": [
                                {
                                    "privateIpv4Address": self.TEST_IP_ADDRESS,
                                },
                            ],
                        }
                    ],
                    "taskArn": self.TEST_TASK_ARN_2,
                },
            ],
            "failures": [],
        }
        self.gw.client.describe_tasks = MagicMock(return_value=client_return_response)
        containers = self.gw.describe_tasks(
            self.TEST_CLUSTER, [self.TEST_TASK_ARN, self.TEST_TASK_ARN_2]
        )
        expected_containers = [
            ContainerInstance(
                self.TEST_TASK_ARN,
                self.TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
            ContainerInstance(
                self.TEST_TASK_ARN_2,
                self.TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
        ]
        self.assertEqual(containers, expected_containers)
        self.gw.client.describe_tasks.assert_called()

    def test_describe_tasks_nonexistent(self) -> None:
        client_return_response = {
            "tasks": [
                {
                    "containers": [
                        {
                            "name": self.TEST_CONTAINER,
                            "exitcode": 123,
                            "lastStatus": "RUNNING",
                            "networkInterfaces": [
                                {
                                    "privateIpv4Address": self.TEST_IP_ADDRESS,
                                },
                            ],
                        }
                    ],
                    "taskArn": self.TEST_TASK_ARN,
                },
                {
                    "containers": [
                        {
                            "name": self.TEST_CONTAINER,
                            "exitcode": 123,
                            "lastStatus": "RUNNING",
                            "networkInterfaces": [
                                {
                                    "privateIpv4Address": self.TEST_IP_ADDRESS,
                                },
                            ],
                        }
                    ],
                    "taskArn": self.TEST_TASK_ARN_2,
                },
            ],
            "failures": [
                {"arn": self.TEST_TASK_ARN_DNE, "reason": "reason", "detail": "detail"},
            ],
        }
        self.gw.client.describe_tasks = MagicMock(return_value=client_return_response)
        containers = self.gw.describe_tasks(
            self.TEST_CLUSTER,
            [self.TEST_TASK_ARN, self.TEST_TASK_ARN_DNE, self.TEST_TASK_ARN_2],
        )
        expected_containers = [
            ContainerInstance(
                self.TEST_TASK_ARN,
                self.TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
            None,
            ContainerInstance(
                self.TEST_TASK_ARN_2,
                self.TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
        ]
        self.assertEqual(containers, expected_containers)
        self.gw.client.describe_tasks.assert_called()

    def test_stop_task(self) -> None:
        client_return_response = {
            "task": {
                "containers": [
                    {
                        "name": self.TEST_CONTAINER,
                        "exitcode": 1,
                        "lastStatus": "STOPPED",
                        "networkInterfaces": [
                            {
                                "privateIpv4Address": self.TEST_IP_ADDRESS,
                            },
                        ],
                    }
                ],
                "taskArn": self.TEST_TASK_ARN,
            }
        }
        self.gw.client.stop_task = MagicMock(return_value=client_return_response)
        self.gw.stop_task(self.TEST_CLUSTER, self.TEST_TASK_ARN)
        self.gw.client.stop_task.assert_called()

    def test_list_tasks(self) -> None:
        client_return_response = {"taskArns": [self.TEST_TASK_ARN]}
        self.gw.client.list_tasks = MagicMock(return_value=client_return_response)
        tasks = self.gw.list_tasks(self.TEST_CLUSTER)
        expected_tasks = [self.TEST_TASK_ARN]
        self.assertEqual(tasks, expected_tasks)
        self.gw.client.list_tasks.assert_called()

    def test_describe_clusers(self) -> None:
        test_tasks = 100
        client_return_response = {
            "clusters": [
                {
                    "clusterArn": self.TEST_CLUSTER,
                    "clusterName": "cluster_1",
                    "tags": [
                        {
                            "key": self.TEST_CLUSTER_TAG_KEY,
                            "value": self.TEST_CLUSTER_TAG_VALUE,
                        },
                    ],
                    "status": "ACTIVE",
                    "pendingTasksCount": test_tasks,
                    "runningTasksCount": test_tasks,
                }
            ]
        }
        self.gw.client.describe_clusters = MagicMock(
            return_value=client_return_response
        )
        clusters = self.gw.describe_clusters(
            clusters=[
                self.TEST_CLUSTER,
            ]
        )
        tags = {self.TEST_CLUSTER_TAG_KEY: self.TEST_CLUSTER_TAG_VALUE}
        expected_clusters = [
            Cluster(
                self.TEST_CLUSTER,
                "cluster_1",
                test_tasks,
                test_tasks,
                ClusterStatus.ACTIVE,
                tags,
            )
        ]
        self.assertEqual(expected_clusters, clusters)
        self.gw.client.describe_clusters.assert_called()

    def test_describe_clusers_by_tags(self) -> None:
        test_tasks = 100
        tags = {self.TEST_CLUSTER_TAG_KEY: self.TEST_CLUSTER_TAG_VALUE}
        client_return_response = {
            "clusters": [
                {
                    "clusterArn": self.TEST_CLUSTER,
                    "clusterName": "cluster_1",
                    "tags": [
                        {
                            "key": self.TEST_CLUSTER_TAG_KEY,
                            "value": self.TEST_CLUSTER_TAG_VALUE,
                        },
                    ],
                    "status": "ACTIVE",
                    "pendingTasksCount": test_tasks,
                    "runningTasksCount": test_tasks,
                }
            ]
        }
        self.gw.client.describe_clusters = MagicMock(
            return_value=client_return_response
        )
        expected_clusters = [
            Cluster(
                self.TEST_CLUSTER,
                "cluster_1",
                test_tasks,
                test_tasks,
                ClusterStatus.ACTIVE,
                tags,
            )
        ]
        self.gw.list_clusters = MagicMock(return_value=[self.TEST_CLUSTER])
        clusters = self.gw.describe_clusters(tags=tags)
        self.assertEqual(expected_clusters, clusters)
        self.gw.client.describe_clusters.assert_called()
        self.gw.list_clusters.assert_called()  # pyre-ignore

    def test_describe_task_definition(self) -> None:
        task_definition_name = "onedocker-task_pce_id"
        test_image = "test_image"
        test_cpu = 4096
        test_memory = 30720
        test_entry_point = ["sh", "-c"]
        test_environment = [{"name": "USER", "value": "ubuntu"}]
        test_task_role = "test-task-role"
        test_tags = [{"key": "pce-id", "value": "zehuali_test"}]
        test_container_name = "container_name"
        test_container_definition_id = get_container_definition_id(
            self.TEST_TASK_DEFINITION_ARN, test_container_name
        )
        client_return_response = {
            "taskDefinition": {
                "taskDefinitionArn": self.TEST_TASK_DEFINITION_ARN,
                "containerDefinitions": [
                    {
                        "name": test_container_name,
                        "image": test_image,
                        "cpu": test_cpu,
                        "memory": test_memory,
                        "entryPoint": test_entry_point,
                        "environment": test_environment,
                    }
                ],
                "taskRoleArn": test_task_role,
            },
            "tags": test_tags,
        }
        self.gw.client.describe_task_definition = MagicMock(
            return_value=client_return_response
        )
        self.gw.client.list_task_definitions = MagicMock(
            return_value={"taskDefinitionArns": [self.TEST_TASK_DEFINITION_ARN]}
        )
        test_tags_dict = convert_list_to_dict(test_tags, "key", "value")
        test_environment_dict = convert_list_to_dict(test_environment, "name", "value")
        container_definition = self.gw.describe_task_definition(task_definition_name)
        container_definitions = self.gw.describe_task_definitions(tags=test_tags_dict)
        expected_container_definition = ContainerDefinition(
            test_container_definition_id,
            test_image,
            test_cpu,
            test_memory,
            test_entry_point,
            test_environment_dict,
            test_task_role,
            test_tags_dict,
        )
        self.assertEqual(expected_container_definition, container_definition)
        self.assertEqual([expected_container_definition], container_definitions)

        self.gw.client.describe_task_definition.assert_called()
        self.gw.client.list_task_definitions.assert_called()
