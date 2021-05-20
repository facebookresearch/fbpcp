#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import AsyncMock, patch

from fbpcs.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcs.service.onedocker import OneDockerService


class TestOneDockerService(unittest.TestCase):
    @patch("fbpcs.service.container.ContainerService")
    def setUp(self, MockContainerService):
        container_svc = MockContainerService()
        self.onedocker_svc = OneDockerService(container_svc)

    def test_start_container(self):
        mocked_container_info = ContainerInstance(
            "arn:aws:ecs:region:account_id:task/container_id",
            "192.0.2.0",
            ContainerInstanceStatus.STARTED,
        )
        self.onedocker_svc.container_svc.create_instances_async = AsyncMock(
            return_value=[mocked_container_info]
        )
        returned_container_info = self.onedocker_svc.start_container(
            "task_def", "project/exe_name", "cmd_args"
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
        self.onedocker_svc.container_svc.create_instances_async = AsyncMock(
            return_value=mocked_container_info
        )
        returned_container_info = self.onedocker_svc.start_containers(
            "task_def", "project/exe_name", ["--k1=v1", "--k2=v2"]
        )
        self.assertEqual(returned_container_info, mocked_container_info)

    def test_get_cmd(self):
        package_name = "project/exe_name"
        cmd_args = "--k1=v1 --k2=v2"
        timeout = 3600
        expected_cmd_without_timeout = "python3.8 -m one_docker_runner --package_name=project/exe_name --cmd='/root/one_docker/package/exe_name --k1=v1 --k2=v2'"
        expected_cmd_with_timeout = expected_cmd_without_timeout + " --timeout=3600"
        cmd_without_timeout = self.onedocker_svc._get_cmd(package_name, cmd_args)
        cmd_with_timeout = self.onedocker_svc._get_cmd(package_name, cmd_args, timeout)
        self.assertEqual(expected_cmd_without_timeout, cmd_without_timeout)
        self.assertEqual(expected_cmd_with_timeout, cmd_with_timeout)
