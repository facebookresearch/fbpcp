#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fbpcs.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcs.error.pcs import PcsError
from fbpcs.service.onedocker import OneDockerService


class TestOneDockerService(unittest.TestCase):
    @patch("fbpcs.service.container.ContainerService")
    def setUp(self, MockContainerService):
        container_svc = MockContainerService()
        self.onedocker_svc = OneDockerService(container_svc, "task_def")

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
        self.onedocker_svc.container_svc.create_instances_async = AsyncMock(
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
        expected_results = [None, PcsError("instance id not found")]
        self.onedocker_svc.container_svc.cancel_instances = MagicMock(
            return_value=expected_results
        )
        self.assertEqual(
            self.onedocker_svc.stop_containers(containers), expected_results
        )
        self.onedocker_svc.container_svc.cancel_instances.assert_called_with(containers)
