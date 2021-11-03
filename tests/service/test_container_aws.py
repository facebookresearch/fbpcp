#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcp.error.pcp import PcpError
from fbpcp.service.container_aws import AWSContainerService

TEST_INSTANCE_ID_1 = "test-instance-id-1"
TEST_INSTANCE_ID_2 = "test-instance-id-2"
TEST_INSTANCE_ID_DNE = "test-instance-id-dne"
TEST_REGION = "us-west-2"
TEST_KEY_ID = "test-key-id"
TEST_KEY_DATA = "test-key-data"
TEST_CLUSTER = "test-cluster"
TEST_SUBNETS = ["test-subnet0", "test-subnet1"]
TEST_IP_ADDRESS = "127.0.0.1"
TEST_CONTAINER_DEFNITION = "test-task-definition#test-container-definition"


class TestAWSContainerService(unittest.TestCase):
    @patch("fbpcp.gateway.ecs.ECSGateway")
    def setUp(self, MockECSGateway):
        self.container_svc = AWSContainerService(
            TEST_REGION, TEST_CLUSTER, TEST_SUBNETS, TEST_KEY_ID, TEST_KEY_DATA
        )
        self.container_svc.ecs_gateway = MockECSGateway()

    def test_create_instances(self):
        created_instances = [
            ContainerInstance(
                TEST_INSTANCE_ID_1,
                TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
            ContainerInstance(
                TEST_INSTANCE_ID_2,
                TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
        ]

        self.container_svc.ecs_gateway.run_task = MagicMock(
            side_effect=created_instances
        )

        cmd_list = ["test_cmd", "test_cmd-1"]
        container_instances = self.container_svc.create_instances(
            TEST_CONTAINER_DEFNITION, cmd_list
        )
        self.assertEqual(container_instances, created_instances)
        self.assertEqual(
            self.container_svc.ecs_gateway.run_task.call_count, len(created_instances)
        )

    def test_create_instance(self):
        created_instance = ContainerInstance(
            TEST_INSTANCE_ID_1,
            TEST_IP_ADDRESS,
            ContainerInstanceStatus.STARTED,
        )

        self.container_svc.ecs_gateway.run_task = MagicMock(
            return_value=created_instance
        )
        container_instance = self.container_svc.create_instance(
            TEST_CONTAINER_DEFNITION, "test-cmd"
        )
        self.assertEqual(container_instance, created_instance)

    def test_get_instance(self):
        container_instance = ContainerInstance(
            TEST_INSTANCE_ID_1,
            TEST_IP_ADDRESS,
            ContainerInstanceStatus.STARTED,
        )
        self.container_svc.ecs_gateway.describe_task = MagicMock(
            return_value=container_instance
        )
        instance = self.container_svc.get_instance(TEST_INSTANCE_ID_1)
        self.assertEqual(instance, container_instance)

    def test_get_instance_nonexistent(self):
        container_instance = None
        self.container_svc.ecs_gateway.describe_task = MagicMock(
            return_value=container_instance
        )
        instance = self.container_svc.get_instance(TEST_INSTANCE_ID_DNE)
        self.assertEqual(instance, container_instance)

    def test_get_instances(self):
        container_instances = [
            ContainerInstance(
                TEST_INSTANCE_ID_1,
                TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
            ContainerInstance(
                TEST_INSTANCE_ID_2,
                TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
        ]
        self.container_svc.ecs_gateway.describe_tasks = MagicMock(
            return_value=container_instances
        )
        instances = self.container_svc.get_instances(
            [TEST_INSTANCE_ID_1, TEST_INSTANCE_ID_2]
        )
        self.assertEqual(instances, container_instances)

    def test_get_instances_nonexistent(self):
        container_instances = [
            ContainerInstance(
                TEST_INSTANCE_ID_1,
                TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
            None,
            ContainerInstance(
                TEST_INSTANCE_ID_2,
                TEST_IP_ADDRESS,
                ContainerInstanceStatus.STARTED,
            ),
        ]

        self.container_svc.ecs_gateway.describe_tasks = MagicMock(
            return_value=container_instances
        )
        instances = self.container_svc.get_instances(
            [TEST_INSTANCE_ID_1, TEST_INSTANCE_ID_DNE, TEST_INSTANCE_ID_2]
        )
        self.assertEqual(instances, container_instances)

    def test_cancel_instances(self):
        instance_ids = [TEST_INSTANCE_ID_1, TEST_INSTANCE_ID_2]
        errors = [None, PcpError("instance id not found")]
        self.container_svc.ecs_gateway.stop_task = MagicMock(side_effect=errors)
        self.assertEqual(self.container_svc.cancel_instances(instance_ids), errors)
