#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcs.entity.cluster_instance import ClusterStatus, Cluster
from fbpcs.entity.container_instance import ContainerInstanceStatus, ContainerInstance
from fbpcs.gateway.ecs import ECSGateway


class TestECSGateway(unittest.TestCase):
    TEST_TASK_ARN = "test-task-arn"
    TEST_TASK_DEFINITION = "test-task-definition"
    TEST_CONTAINER = "test-container"
    TEST_CLUSTER = "test-cluster"
    TEST_CMD = "test-cmd"
    TEST_SUBNET = "test-subnet"
    TEST_ACCESS_KEY_ID = "test-access-key-id"
    TEST_ACCESS_KEY_DATA = "test-access-key-data"
    TEST_IP_ADDRESS = "127.0.0.1"
    TEST_FILE = "test-file"
    TEST_CLUSTER_TAG_KEY = "test-tag-key"
    TEST_CLUSTER_TAG_VALUE = "test-tag-value"
    REGION = "us-west-2"

    @patch("boto3.client")
    def setUp(self, BotoClient):
        self.gw = ECSGateway(
            self.REGION, self.TEST_ACCESS_KEY_ID, self.TEST_ACCESS_KEY_DATA
        )
        self.gw.client = BotoClient()

    def test_run_task(self):
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
            self.TEST_SUBNET,
        )
        expected_task = ContainerInstance(
            self.TEST_TASK_ARN,
            self.TEST_IP_ADDRESS,
            ContainerInstanceStatus.STARTED,
        )
        self.assertEqual(task, expected_task)
        self.gw.client.run_task.assert_called()

    def test_describe_tasks(self):
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
            ]
        }
        self.gw.client.describe_tasks = MagicMock(return_value=client_return_response)
        tasks = [
            self.TEST_TASK_DEFINITION,
        ]
        tasks = self.gw.describe_tasks(self.TEST_CLUSTER, tasks)
        expected_tasks = [
            ContainerInstance(
                self.TEST_TASK_ARN,
                self.TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
        ]
        self.assertEqual(tasks, expected_tasks)
        self.gw.client.describe_tasks.assert_called()

    def test_stop_task(self):
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

    def test_list_tasks(self):
        client_return_response = {"taskArns": [self.TEST_TASK_ARN]}
        self.gw.client.list_tasks = MagicMock(return_value=client_return_response)
        tasks = self.gw.list_tasks(self.TEST_CLUSTER)
        expected_tasks = [self.TEST_TASK_ARN]
        self.assertEqual(tasks, expected_tasks)
        self.gw.client.list_tasks.assert_called()

    def test_describe_clusers(self):
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
                }
            ]
        }
        self.gw.client.describe_clusters = MagicMock(
            return_value=client_return_response
        )
        clusters = self.gw.describe_clusters(
            [
                self.TEST_CLUSTER,
            ]
        )
        tags = {self.TEST_CLUSTER_TAG_KEY: self.TEST_CLUSTER_TAG_VALUE}
        expected_clusters = [
            Cluster(self.TEST_CLUSTER, "cluster_1", ClusterStatus.ACTIVE, tags)
        ]
        self.assertEqual(expected_clusters, clusters)
        self.gw.client.describe_clusters.assert_called()
