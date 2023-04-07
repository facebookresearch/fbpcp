#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import unittest
from shlex import quote
from typing import List
from unittest import IsolatedAsyncioTestCase
from unittest.mock import ANY, AsyncMock, call, MagicMock, patch

from fbpcp.entity.certificate_request import CertificateRequest, KeyAlgorithm
from fbpcp.entity.cloud_provider import CloudProvider
from fbpcp.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcp.entity.container_permission import ContainerPermissionConfig
from fbpcp.entity.container_type import ContainerType, ContainerTypeConfig
from fbpcp.error.pcp import PcpError
from fbpcp.service.onedocker import (
    METRICS_START_CONTAINERS_COUNT,
    METRICS_START_CONTAINERS_DURATION,
    ONEDOCKER_CMD_PREFIX,
    OneDockerService,
)

TEST_INSTANCE_ID_1 = "test-instance-id-1"
TEST_INSTANCE_ID_2 = "test-instance-id-2"
TEST_IP_ADDRESS = "127.0.0.1"
TEST_VERSION = "rc"
TEST_ENV_VARS = {"test_name": "test_value"}
TEST_ENV_VARS_2 = {"test_name_2": "test_value_2"}
TEST_ENV_VARS_LIST = [TEST_ENV_VARS, TEST_ENV_VARS_2]
TEST_PACKAGE_NAME = "project/exe_name"
TEST_TASK_DEF = "task_def"
TEST_CMD_ARGS_LIST = ["--k1=v1", "--k2=v2"]
TEST_TIMEOUT = 3600
TEST_TAG = "test"
TEST_KEY_ALGORITHM = KeyAlgorithm.RSA
TEST_KEY_SIZE = 4096
TEST_PASSPHRASE = "test"
TEST_ORGANIZATION_NAME = "Test Company"
TEST_COUNTRY_NAME = "US"
TEST_CLUSTER_STR = "Test Cluster"
TEST_CLOUD_PROVIDER: CloudProvider = CloudProvider.AWS
TEST_CONTAINER_TYPE: ContainerType = ContainerType.LARGE
TEST_CONTAINER_CONFIG: ContainerTypeConfig = ContainerTypeConfig.get_config(
    TEST_CLOUD_PROVIDER, TEST_CONTAINER_TYPE
)
TEST_OPA_WORKFLOW_PATH = "/folder/file.json"
TEST_PERMISSION: ContainerPermissionConfig = ContainerPermissionConfig("test-role-id")
TEST_TIME = float(1680805642.80)
TEST_EXIT_CODE = 0
TEST_CLASS_NAME = "ContainerInsight"


class TestOneDockerServiceSync(unittest.TestCase):
    @patch("fbpcp.metrics.emitter.MetricsEmitter")
    @patch("fbpcp.service.container.ContainerService")
    @patch("fbpcp.service.insights.InsightsService")
    def setUp(self, MockContainerService, MockMetricsEmitter, MockInsightsService):
        self.container_svc = MockContainerService()
        self.metrics = MockMetricsEmitter()
        self.insights = MockInsightsService()
        self.onedocker_svc = OneDockerService(
            container_svc=self.container_svc,
            task_definition=TEST_TASK_DEF,
            metrics=self.metrics,
            insights=self.insights,
        )

    def test_start_container(self):
        # Arrange
        mocked_container_info: ContainerInstance = _get_pending_container_instances()[0]
        self.container_svc.create_instances = MagicMock(
            return_value=[mocked_container_info]
        )
        # Act
        returned_container_info: ContainerInstance = self.onedocker_svc.start_container(
            task_definition=TEST_TASK_DEF,
            package_name=TEST_PACKAGE_NAME,
            cmd_args=TEST_CMD_ARGS_LIST[0],
            certificate_request=None,
            container_type=TEST_CONTAINER_TYPE,
            opa_workflow_path=TEST_OPA_WORKFLOW_PATH,
            permission=TEST_PERMISSION,
        )
        # Assert
        self.assertEqual(returned_container_info, mocked_container_info)
        self.container_svc.create_instances.assert_called_with(
            container_definition=TEST_TASK_DEF,
            cmds=ANY,
            env_vars=ANY,
            container_type=TEST_CONTAINER_TYPE,
            permission=TEST_PERMISSION,
        )

    def test_start_containers(self):
        # Arrange
        mocked_container_info = _get_pending_container_instances()
        self.container_svc.create_instances = MagicMock(
            return_value=mocked_container_info
        )
        test_cert_request = CertificateRequest(
            key_algorithm=TEST_KEY_ALGORITHM,
            key_size=TEST_KEY_SIZE,
            passphrase=TEST_PASSPHRASE,
            cert_folder=None,
            private_key_name=None,
            certificate_name=None,
            days_valid=None,
            country_name=TEST_COUNTRY_NAME,
            state_or_province_name=None,
            locality_name=None,
            organization_name=None,
            common_name=None,
            dns_name=None,
        )

        calls = [
            call(
                TEST_PACKAGE_NAME,
                TEST_VERSION,
                TEST_CMD_ARGS_LIST[0],
                TEST_TIMEOUT,
                test_cert_request,
                TEST_OPA_WORKFLOW_PATH,
            ),
            call(
                TEST_PACKAGE_NAME,
                TEST_VERSION,
                TEST_CMD_ARGS_LIST[1],
                TEST_TIMEOUT,
                test_cert_request,
                TEST_OPA_WORKFLOW_PATH,
            ),
        ]
        self.onedocker_svc._get_cmd = MagicMock()

        # Act
        returned_container_info: List[
            ContainerInstance
        ] = self.onedocker_svc.start_containers(
            task_definition=TEST_TASK_DEF,
            package_name=TEST_PACKAGE_NAME,
            cmd_args_list=TEST_CMD_ARGS_LIST,
            version=TEST_VERSION,
            env_vars=TEST_ENV_VARS,
            timeout=TEST_TIMEOUT,
            certificate_request=test_cert_request,
            container_type=TEST_CONTAINER_TYPE,
            opa_workflow_path=TEST_OPA_WORKFLOW_PATH,
            permission=TEST_PERMISSION,
        )

        # Assert
        self.onedocker_svc._get_cmd.assert_has_calls(calls, any_order=False)
        self.assertEqual(returned_container_info, mocked_container_info)

    @patch.object(OneDockerService, "_get_cmd")
    def test_start_containers_with_env_var_list(self, mock_get_cmd):
        # Arrange
        mocked_container_info = _get_pending_container_instances()
        self.container_svc.create_instances = MagicMock(
            return_value=mocked_container_info
        )
        expected_cmd = ["test_cmd_1", "test_cmd_2"]
        mock_get_cmd.side_effect = expected_cmd

        # Act
        returned_container_info: List[
            ContainerInstance
        ] = self.onedocker_svc.start_containers(
            task_definition=TEST_TASK_DEF,
            package_name=TEST_PACKAGE_NAME,
            cmd_args_list=TEST_CMD_ARGS_LIST,
            version=TEST_VERSION,
            env_vars=TEST_ENV_VARS_LIST,
            timeout=TEST_TIMEOUT,
            container_type=TEST_CONTAINER_TYPE,
        )

        # Assert
        self.assertEqual(returned_container_info, mocked_container_info)
        self.container_svc.create_instances.assert_called_with(
            container_definition=TEST_TASK_DEF,
            cmds=expected_cmd,
            env_vars=TEST_ENV_VARS_LIST,
            container_type=TEST_CONTAINER_TYPE,
            permission=None,
        )

    def test_start_containers_throw_with_invalid_env_var_list(self):
        # Act & Assert
        with self.assertRaises(ValueError):
            self.onedocker_svc.start_containers(
                task_definition=TEST_TASK_DEF,
                package_name=TEST_PACKAGE_NAME,
                cmd_args_list=TEST_CMD_ARGS_LIST,
                version=TEST_VERSION,
                env_vars=[TEST_ENV_VARS],
                timeout=TEST_TIMEOUT,
                container_type=TEST_CONTAINER_TYPE,
                permission=None,
            )
        with self.assertRaises(ValueError):
            self.onedocker_svc.start_containers(
                task_definition=TEST_TASK_DEF,
                package_name=TEST_PACKAGE_NAME,
                cmd_args_list=TEST_CMD_ARGS_LIST,
                version=TEST_VERSION,
                env_vars=[],
                timeout=TEST_TIMEOUT,
                container_type=TEST_CONTAINER_TYPE,
                permission=None,
            )

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

    def test_get_cmd_with_certificate_request(self):
        # Arrange
        test_cert_request = CertificateRequest(
            key_algorithm=TEST_KEY_ALGORITHM,
            key_size=TEST_KEY_SIZE,
            passphrase=TEST_PASSPHRASE,
            cert_folder=None,
            private_key_name=None,
            certificate_name=None,
            days_valid=None,
            country_name=TEST_COUNTRY_NAME,
            state_or_province_name=None,
            locality_name=None,
            organization_name=None,
            common_name=None,
            dns_name=None,
        )
        import json

        cert_params = json.dumps(
            {
                "key_algorithm": TEST_KEY_ALGORITHM.value,
                "key_size": TEST_KEY_SIZE,
                "passphrase": TEST_PASSPHRASE,
                "country_name": TEST_COUNTRY_NAME,
            }
        )
        expected_cmd = f"python3.8 -m onedocker.script.runner {TEST_PACKAGE_NAME} --exe_args={quote(str(TEST_CMD_ARGS_LIST[0]))} --version={quote(str(TEST_VERSION))} --timeout={quote(str(TEST_TIMEOUT))} --cert_params={quote(str(cert_params))}"

        # Act
        result = self.onedocker_svc._get_cmd(
            TEST_PACKAGE_NAME,
            TEST_VERSION,
            TEST_CMD_ARGS_LIST[0],
            TEST_TIMEOUT,
            test_cert_request,
        )

        # Assert
        self.assertEqual(result, expected_cmd)

    def test_get_cmd_with_opa_workflow_path(self):
        # Arrange
        expected_runner_args = f"--exe_args={quote(str(TEST_CMD_ARGS_LIST[0]))} --version={quote(str(TEST_VERSION))} --timeout={quote(str(TEST_TIMEOUT))} --opa_workflow_path={TEST_OPA_WORKFLOW_PATH}"
        expected_cmd = ONEDOCKER_CMD_PREFIX.format(
            package_name=TEST_PACKAGE_NAME,
            runner_args=expected_runner_args,
        ).strip()

        # Act
        result = self.onedocker_svc._get_cmd(
            package_name=TEST_PACKAGE_NAME,
            version=TEST_VERSION,
            cmd_args=TEST_CMD_ARGS_LIST[0],
            timeout=TEST_TIMEOUT,
            opa_workflow_path=TEST_OPA_WORKFLOW_PATH,
        )

        # Assert
        self.assertEqual(result, expected_cmd)

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

    def test_metrics(self):
        self.container_svc.create_instances = MagicMock(
            return_value=_get_pending_container_instances()
        )
        TEST_CERTIFICATE_REQUEST = None
        calls = [
            call(
                TEST_PACKAGE_NAME,
                TEST_VERSION,
                TEST_CMD_ARGS_LIST[0],
                TEST_TIMEOUT,
                TEST_CERTIFICATE_REQUEST,
                TEST_OPA_WORKFLOW_PATH,
            ),
            call(
                TEST_PACKAGE_NAME,
                TEST_VERSION,
                TEST_CMD_ARGS_LIST[1],
                TEST_TIMEOUT,
                TEST_CERTIFICATE_REQUEST,
                TEST_OPA_WORKFLOW_PATH,
            ),
        ]
        self.onedocker_svc._get_cmd = MagicMock()
        self.onedocker_svc.start_containers(
            package_name=TEST_PACKAGE_NAME,
            task_definition=TEST_TASK_DEF,
            cmd_args_list=TEST_CMD_ARGS_LIST,
            version=TEST_VERSION,
            timeout=TEST_TIMEOUT,
            certificate_request=TEST_CERTIFICATE_REQUEST,
            opa_workflow_path=TEST_OPA_WORKFLOW_PATH,
        )
        self.onedocker_svc._get_cmd.assert_has_calls(calls, any_order=False)

        self.metrics.count.assert_any_call(ANY, 2)
        self.metrics.count.assert_any_call(METRICS_START_CONTAINERS_COUNT, 1)
        self.metrics.gauge.assert_called_with(METRICS_START_CONTAINERS_DURATION, ANY)

    def test_get_container(self):
        # Arrange
        expected_results = _get_pending_container_instances()[0]

        self.container_svc.get_instance = MagicMock(return_value=expected_results)

        # Act
        container = self.onedocker_svc.get_container(TEST_INSTANCE_ID_1)

        # Assert
        self.assertEqual(container, expected_results)
        self.container_svc.get_instance.assert_called_with(TEST_INSTANCE_ID_1)

    def test_get_containers(self):
        # Arrange
        expected_results = _get_pending_container_instances()

        self.container_svc.get_instances = MagicMock(return_value=expected_results)

        # Act
        containers = self.onedocker_svc.get_containers(
            [TEST_INSTANCE_ID_1, TEST_INSTANCE_ID_2]
        )

        # Assert
        self.assertEqual(containers, expected_results)
        self.container_svc.get_instances.assert_called_with(
            [TEST_INSTANCE_ID_1, TEST_INSTANCE_ID_2]
        )

    def test_get_cluster(self):
        # Arrange
        expected_result = TEST_CLUSTER_STR
        self.container_svc.get_cluster.return_value = expected_result

        # Act
        cluster = self.onedocker_svc.get_cluster()

        # Assert
        self.assertEqual(cluster, expected_result)
        self.container_svc.get_cluster.assert_called_with()

    @patch("time.time", MagicMock(return_value=TEST_TIME))
    def test_get_insight(self):
        #  Arrange
        container_instance = ContainerInstance(
            instance_id=TEST_INSTANCE_ID_1,
            ip_address=TEST_IP_ADDRESS,
            status=ContainerInstanceStatus.STARTED,
            cpu=TEST_CONTAINER_CONFIG.cpu,
            memory=TEST_CONTAINER_CONFIG.memory,
            exit_code=TEST_EXIT_CODE,
        )
        self.container_svc.get_cluster.return_value = TEST_CLUSTER_STR

        expected_result = json.dumps(
            {
                "time": TEST_TIME,
                "cluster_name": TEST_CLUSTER_STR,
                "instance_id": TEST_INSTANCE_ID_1,
                "status": "STARTED",
                "exit_code": TEST_EXIT_CODE,
                "class_name": TEST_CLASS_NAME,
            }
        )

        # Act
        insight = self.onedocker_svc._get_insight(container_instance)

        # Assert
        self.assertEqual(insight, expected_result)

    @patch("time.time", MagicMock(return_value=TEST_TIME))
    def test_insights_emit(self):
        # Arrange
        self.container_svc.create_instances = MagicMock(
            return_value=_get_pending_container_instances()
        )
        self.container_svc.get_cluster.return_value = TEST_CLUSTER_STR

        calls = [
            call(
                json.dumps(
                    {
                        "time": TEST_TIME,
                        "cluster_name": TEST_CLUSTER_STR,
                        "instance_id": TEST_INSTANCE_ID_1,
                        "status": "UNKNOWN",
                        "exit_code": None,
                        "class_name": TEST_CLASS_NAME,
                    }
                )
            ),
            call(
                json.dumps(
                    {
                        "time": TEST_TIME,
                        "cluster_name": TEST_CLUSTER_STR,
                        "instance_id": TEST_INSTANCE_ID_2,
                        "status": "UNKNOWN",
                        "exit_code": None,
                        "class_name": TEST_CLASS_NAME,
                    }
                )
            ),
        ]

        # Act
        self.onedocker_svc.start_containers(
            package_name=TEST_PACKAGE_NAME,
            cmd_args_list=TEST_CMD_ARGS_LIST,
        )
        # Assert
        self.insights.emit.assert_has_calls(calls)


class TestOneDockerServiceAsync(IsolatedAsyncioTestCase):
    @patch("fbpcp.service.container.ContainerService")
    def setUp(self, MockContainerService):
        self.container_svc = MockContainerService()
        self.insights = AsyncMock()
        self.onedocker_svc = OneDockerService(
            container_svc=self.container_svc,
            task_definition=TEST_TASK_DEF,
            insights=self.insights,
        )

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

    @patch("time.time", MagicMock(return_value=TEST_TIME))
    async def test_insights_emit_async(self):
        # Arrange
        running_containers = _get_running_container_instances()
        pending_containers = _get_pending_container_instances()

        self.onedocker_svc.get_containers = MagicMock(
            side_effect=([running_containers[0]], [running_containers[1]])
        )

        self.container_svc.get_cluster.return_value = TEST_CLUSTER_STR

        calls = [
            call(
                json.dumps(
                    {
                        "time": TEST_TIME,
                        "cluster_name": TEST_CLUSTER_STR,
                        "instance_id": TEST_INSTANCE_ID_1,
                        "status": "STARTED",
                        "exit_code": None,
                        "class_name": TEST_CLASS_NAME,
                    }
                )
            ),
            call(
                json.dumps(
                    {
                        "time": TEST_TIME,
                        "cluster_name": TEST_CLUSTER_STR,
                        "instance_id": TEST_INSTANCE_ID_2,
                        "status": "STARTED",
                        "exit_code": None,
                        "class_name": TEST_CLASS_NAME,
                    }
                )
            ),
        ]

        # Act
        await self.onedocker_svc.wait_for_pending_containers(
            [container.instance_id for container in pending_containers]
        )

        # Assert
        self.insights.emit_async.assert_has_calls(calls)


def _get_pending_container_instances() -> List[ContainerInstance]:
    return [
        ContainerInstance(
            TEST_INSTANCE_ID_1,
            TEST_IP_ADDRESS,
            ContainerInstanceStatus.UNKNOWN,
            cpu=TEST_CONTAINER_CONFIG.cpu,
            memory=TEST_CONTAINER_CONFIG.memory,
        ),
        ContainerInstance(
            TEST_INSTANCE_ID_2,
            TEST_IP_ADDRESS,
            ContainerInstanceStatus.UNKNOWN,
            cpu=TEST_CONTAINER_CONFIG.cpu,
            memory=TEST_CONTAINER_CONFIG.memory,
        ),
    ]


def _get_running_container_instances() -> List[ContainerInstance]:
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
