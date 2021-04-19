#!/usr/bin/env python3

import unittest

from entity.cluster_instance import ClusterStatus, Cluster
from entity.container_instance import ContainerInstanceStatus, ContainerInstance
from mapper.aws import (
    map_ecstask_to_containerinstance,
    map_esccluster_to_clusterinstance,
)


class TestAWSMapper(unittest.TestCase):
    TEST_IP_ADDRESS = "127.0.0.1"
    TEST_TASK_ARN = "test-task-arn"
    TEST_CLUSTER_ARN = "test-cluster-arn"
    TEST_CLUSTER_NAME = "test-cluster-name"

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
        ecs_cluster_response = {
            "clusters": [
                {
                    "clusterName": self.TEST_CLUSTER_NAME,
                    "clusterArn": self.TEST_CLUSTER_ARN,
                    "status": "ACTIVE",
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
                ClusterStatus.ACTIVE,
                multi_tag_value_pair,
            ),
            Cluster(
                self.TEST_CLUSTER_ARN,
                self.TEST_CLUSTER_NAME,
                ClusterStatus.INACTIVE,
                single_tag_value_pair,
            ),
            Cluster(
                self.TEST_CLUSTER_ARN,
                self.TEST_CLUSTER_NAME,
                ClusterStatus.UNKNOWN,
                single_tag_value_pair,
            ),
        ]
        cluster_list = [
            map_esccluster_to_clusterinstance(cluster)
            for cluster in ecs_cluster_response["clusters"]
        ]

        self.assertEqual(cluster_list, expected_cluster_list)
