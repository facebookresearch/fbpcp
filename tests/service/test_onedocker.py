#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest import mock, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch, ANY

from fbpcp.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcp.error.pcp import PcpError
from fbpcp.service.onedocker import (
    OneDockerService,
    METRICS_START_CONTAINERS_COUNT,
    METRICS_START_CONTAINERS_DURATION,
)


class TestOneDockerServiceSync(unittest.TestCase):
    @patch("fbpcp.service.container.ContainerService")
    def setUp(self, MockContainerService):
        self.container_svc = MockContainerService()
        self.onedocker_svc = OneDockerService(self.container_svc, "task_def")

    def test_start_container(self):
        mocked_container_info = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id",
            "192.0.2.0",
            ContainerInstanceStatus.STARTED,
        )
        self.container_svc.create_instances_async = AsyncMock(
            return_value=[mocked_container_info]
        )
        returned_container_info = self.onedocker_svc.start_container(
            task_definition="task_def",
            package_name="project/exe_name",
            cmd_args="cmd_args",
        )
        self.assertEqual(returned_container_info, mocked_container_info)

    def test_start_containers(self):
        mocked_container_info = [
            ContainerInstance(
                "arn:aws:ecs:region:account_id:task/container_id_1",
                "192.0.2.0",
                ContainerInstanceStatus.STARTED,
            ),
            ContainerInstance(
                "arn:aws:ecs:region:account_id:task/container_id_2",
                "192.0.2.1",
                ContainerInstanceStatus.STARTED,
            ),
        ]
        self.container_svc.create_instances_async = AsyncMock(
            return_value=mocked_container_info
        )
        returned_container_info = self.onedocker_svc.start_containers(
            task_definition="task_def",
            package_name="project/exe_name",
            cmd_args_list=["--k1=v1", "--k2=v2"],
        )
        self.assertEqual(returned_container_info, mocked_container_info)

    def test_get_cmd(self):
        package_name = "project/exe_name"
        cmd_args = "--k1=v1 --k2=v2"
        timeout = 3600
        version = "0.1.0"
        expected_cmd_without_arguments = (
            "python3.8 -m onedocker.script.runner project/exe_name --version=latest"
        )
        expected_cmd_with_arguments = f"python3.8 -m onedocker.script.runner project/exe_name --exe_args='{cmd_args}' --version={version} --timeout={timeout}"
        cmd_without_arguments = self.onedocker_svc._get_cmd(package_name)
        cmd_with_arguments = self.onedocker_svc._get_cmd(
            package_name, version, cmd_args, timeout
        )
        self.assertEqual(expected_cmd_without_arguments, cmd_without_arguments)
        self.assertEqual(expected_cmd_with_arguments, cmd_with_arguments)

    def test_stop_containers(self):
        containers = [
            "0cc43cdb-3bee-4407-9c26-c0e6ea5bee84",
            "6b809ef6-c67e-4467-921f-ee261c15a0a2",
        ]
        expected_results = [None, PcpError("instance id not found")]
        self.container_svc.cancel_instances = MagicMock(return_value=expected_results)
        self.assertEqual(
            self.onedocker_svc.stop_containers(containers), expected_results
        )
        self.container_svc.cancel_instances.assert_called_with(containers)


class TestOneDockerServiceAsync(IsolatedAsyncioTestCase):
    @patch("fbpcp.service.container.ContainerService")
    def setUp(self, MockContainerService):
        self.container_svc = MockContainerService()
        self.onedocker_svc = OneDockerService(self.container_svc, "task_def")

    @patch("fbpcp.metrics.emitter.MetricsEmitter")
    async def test_metrics(self, MockMetricsEmitter):
        metrics = MockMetricsEmitter()
        one_docker = OneDockerService(container_svc=self.container_svc, metrics=metrics)
        mocked_container_info = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id",
            "192.0.2.0",
            ContainerInstanceStatus.STARTED,
        )
        self.container_svc.create_instances_async = AsyncMock(
            return_value=[mocked_container_info]
        )

        await one_docker.start_containers_async(
            package_name="project/exe_name",
            task_definition="task_def",
            cmd_args_list=["cmd_args"],
        )

        metrics.count.assert_any_call(ANY, 1)
        metrics.count.assert_any_call(METRICS_START_CONTAINERS_COUNT, 1)
        metrics.gauge.assert_called_with(METRICS_START_CONTAINERS_DURATION, ANY)

    @mock.patch("fbpcp.service.onedocker.OneDockerService.get_containers")
    async def test_wait_for_containers_success(self, get_containers):
        container_1_start = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id_1",
            "192.0.2.0",
            ContainerInstanceStatus.STARTED,
        )
        container_2_start = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id_2",
            "192.0.2.1",
            ContainerInstanceStatus.STARTED,
        )

        container_1_complete = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id_1",
            "192.0.2.0",
            ContainerInstanceStatus.COMPLETED,
        )

        container_2_complete = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id_2",
            "192.0.2.1",
            ContainerInstanceStatus.COMPLETED,
        )

        get_containers.side_effect = [
            [container_1_start],
            [container_1_complete],
            [container_2_complete],
        ]

        containers = [
            container_1_start,
            container_2_start,
        ]

        wait_for_true = await self.onedocker_svc.wait_for_containers_async(
            containers, poll=0
        )

        self.assertTrue(wait_for_true)
        self.assertEqual(containers[0], container_1_complete)
        self.assertEqual(containers[1], container_2_complete)

    @mock.patch("fbpcp.service.onedocker.OneDockerService.get_containers")
    async def test_wait_for_containers_fail(self, get_containers):
        container_1_start = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id_1",
            "192.0.2.0",
            ContainerInstanceStatus.STARTED,
        )
        container_2_start = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id_2",
            "192.0.2.1",
            ContainerInstanceStatus.STARTED,
        )

        container_1_complete = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id_1",
            "192.0.2.0",
            ContainerInstanceStatus.COMPLETED,
        )

        container_2_fail = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id_2",
            "192.0.2.1",
            ContainerInstanceStatus.FAILED,
        )

        get_containers.side_effect = [
            [container_1_start],
            [container_1_complete],
            [container_2_fail],
        ]

        containers = [
            container_1_start,
            container_2_start,
        ]

        wait_for_false = await self.onedocker_svc.wait_for_containers_async(
            containers, poll=0
        )

        self.assertFalse(wait_for_false)
        self.assertEqual(containers[0], container_1_complete)
        self.assertEqual(containers[1], container_2_fail)
