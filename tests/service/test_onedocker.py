#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, call, MagicMock, patch, ANY

from fbpcp.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcp.error.pcp import PcpError
from fbpcp.service.onedocker import (
    OneDockerService,
    METRICS_START_CONTAINERS_COUNT,
    METRICS_START_CONTAINERS_DURATION,
)

TEST_INSTANCE_ID_1 = "test-instance-id-1"
TEST_INSTANCE_ID_2 = "test-instance-id-2"
TEST_IP_ADDRESS = "127.0.0.1"
TEST_VERSION = "rc"
TEST_ENV_VARS = {"test_name": "test_value"}
TEST_PACKAGE_NAME = "project/exe_name"
TEST_TASK_DEF = "task_def"
TEST_CMD_ARGS_LIST = ["--k1=v1", "--k2=v2"]
TEST_TIMEOUT = 3600
TEST_TAG = "test"


class TestOneDockerServiceSync(unittest.TestCase):
    @patch("fbpcp.service.container.ContainerService")
    def setUp(self, MockContainerService):
        self.container_svc = MockContainerService()
        self.onedocker_svc = OneDockerService(self.container_svc, TEST_TASK_DEF)

    def test_start_container(self):
        mocked_container_info = _get_pending_container_instances()[0]
        self.container_svc.create_instances = MagicMock(
            return_value=[mocked_container_info]
        )
        returned_container_info = self.onedocker_svc.start_container(
            task_definition=TEST_TASK_DEF,
            package_name=TEST_PACKAGE_NAME,
            cmd_args=TEST_CMD_ARGS_LIST[0],
        )
        self.assertEqual(returned_container_info, mocked_container_info)

    def test_start_containers(self):
        mocked_container_info = _get_pending_container_instances()
        self.container_svc.create_instances = MagicMock(
            return_value=mocked_container_info
        )
        calls = [
            call(TEST_PACKAGE_NAME, TEST_VERSION, TEST_CMD_ARGS_LIST[0], TEST_TIMEOUT),
            call(TEST_PACKAGE_NAME, TEST_VERSION, TEST_CMD_ARGS_LIST[1], TEST_TIMEOUT),
        ]
        self.onedocker_svc._get_cmd = MagicMock()
        returned_container_info = self.onedocker_svc.start_containers(
            task_definition=TEST_TASK_DEF,
            package_name=TEST_PACKAGE_NAME,
            cmd_args_list=TEST_CMD_ARGS_LIST,
            version=TEST_VERSION,
            env_vars=TEST_ENV_VARS,
            timeout=TEST_TIMEOUT,
        )
        self.onedocker_svc._get_cmd.assert_has_calls(calls, any_order=False)
        self.assertEqual(returned_container_info, mocked_container_info)

    def test_get_cmd(self):
        expected_cmd_without_arguments = (
            f"python3.8 -m onedocker.script.runner {TEST_PACKAGE_NAME} --version=latest"
        )
        expected_cmd_with_arguments = f"python3.8 -m onedocker.script.runner {TEST_PACKAGE_NAME} --exe_args={TEST_CMD_ARGS_LIST[0]} --version={TEST_VERSION} --timeout={TEST_TIMEOUT}"
        cmd_without_arguments = self.onedocker_svc._get_cmd(TEST_PACKAGE_NAME)
        cmd_with_arguments = self.onedocker_svc._get_cmd(
            TEST_PACKAGE_NAME, TEST_VERSION, TEST_CMD_ARGS_LIST[0], TEST_TIMEOUT
        )
        self.assertEqual(expected_cmd_without_arguments, cmd_without_arguments)
        self.assertEqual(expected_cmd_with_arguments, cmd_with_arguments)

    def test_stop_containers(self):
        containers = [
            TEST_INSTANCE_ID_1,
            TEST_INSTANCE_ID_2,
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
        self.onedocker_svc = OneDockerService(self.container_svc, TEST_TASK_DEF)

    @patch("fbpcp.metrics.emitter.MetricsEmitter")
    async def test_metrics(self, MockMetricsEmitter):
        metrics = MockMetricsEmitter()
        onedocker_svc = OneDockerService(
            container_svc=self.container_svc, metrics=metrics
        )
        self.container_svc.create_instances = MagicMock(
            return_value=_get_pending_container_instances()
        )

        onedocker_svc.wait_for_pending_containers = AsyncMock(
            return_value=_get_running_container_instances()
        )

        calls = [
            call(TEST_PACKAGE_NAME, TEST_VERSION, TEST_CMD_ARGS_LIST[0], TEST_TIMEOUT),
            call(TEST_PACKAGE_NAME, TEST_VERSION, TEST_CMD_ARGS_LIST[1], TEST_TIMEOUT),
        ]
        onedocker_svc._get_cmd = MagicMock()
        await onedocker_svc.start_containers_async(
            package_name=TEST_PACKAGE_NAME,
            task_definition=TEST_TASK_DEF,
            cmd_args_list=TEST_CMD_ARGS_LIST,
            version=TEST_VERSION,
            timeout=TEST_TIMEOUT,
        )
        onedocker_svc._get_cmd.assert_has_calls(calls, any_order=False)

        metrics.count.assert_any_call(ANY, 2)
        metrics.count.assert_any_call(METRICS_START_CONTAINERS_COUNT, 1)
        metrics.gauge.assert_called_with(METRICS_START_CONTAINERS_DURATION, ANY)

    async def test_waiting_for_pending_container(self):
        pending_containers = _get_pending_container_instances()
        running_containers = _get_running_container_instances()
        self.onedocker_svc.get_containers = MagicMock(return_value=running_containers)
        expected_container = await self.onedocker_svc.wait_for_pending_container(
            pending_containers[0].instance_id
        )
        self.assertEqual(expected_container, running_containers[0])

    async def test_waiting_for_pending_containers(self):
        pending_containers = _get_pending_container_instances()
        running_containers = _get_running_container_instances()
        self.onedocker_svc.get_containers = MagicMock(
            side_effect=([running_containers[0]], [running_containers[1]])
        )
        expected_containers = await self.onedocker_svc.wait_for_pending_containers(
            [container.instance_id for container in pending_containers]
        )
        self.assertEqual(expected_containers, running_containers)


def _get_pending_container_instances():
    return [
        ContainerInstance(
            TEST_INSTANCE_ID_1,
            TEST_IP_ADDRESS,
            ContainerInstanceStatus.UNKNOWN,
        ),
        ContainerInstance(
            TEST_INSTANCE_ID_2,
            TEST_IP_ADDRESS,
            ContainerInstanceStatus.UNKNOWN,
        ),
    ]


def _get_running_container_instances():
    return [
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
