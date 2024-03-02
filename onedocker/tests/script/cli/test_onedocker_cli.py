#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import os
import sys
import unittest
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import yaml

# pyre-ignore[21]
from docopt import docopt, DocoptExit
from fbpcp.entity.container_instance import ContainerInstanceStatus
from fbpcp.service.container_aws import AWSContainerService
from fbpcp.service.log_cloudwatch import CloudWatchLogService
from fbpcp.service.onedocker import OneDockerService
from fbpcp.util import yaml as util_yaml
from onedocker.entity.package_info import PackageInfo
from onedocker.repository.onedocker_package import OneDockerPackageRepository
from onedocker.script.cli.onedocker_cli import __doc__ as __onedocker_cli_doc__, main


class TestOnedockerCli(unittest.TestCase):
    def setUp(self):
        self.test_config_dict = self._get_test_config_dict()

        self.package_name = "foo"
        self.package_path = "test/bar/"
        self.version = "baz"
        self.config_file = "test_config_file.yml"
        self.timeout = "100"
        self.cmd_args = "-h"
        self.container = "secret_container"

        self.package_info = PackageInfo(
            package_name=self.package_name,
            version=self.version,
            last_modified="Sun Jan 01 01:01:05 2022",
            package_size=1048576,
        )

        self.base_args = {
            "upload": False,
            "archive": False,
            "test": False,
            "show": False,
            "stop": False,
            "--help": False,
            "--verbose": False,
            "--package_name": None,
            "--version": None,
            "--package_path": None,
            "--config": None,
            "--log_path": None,
            "--cmd_args": None,
            "--timeout": None,
            "--container": None,
        }

        # mock objects for functions
        self.mockYamlLoad = patch.object(
            util_yaml,
            "load",
            MagicMock(return_value=self.test_config_dict),
        ).start()

        self.mockODPRUpload = patch.object(
            OneDockerPackageRepository,
            "upload",
            MagicMock(return_value=None),
        ).start()

        self.mockODPRArchive = patch.object(
            OneDockerPackageRepository,
            "archive_package",
            MagicMock(return_value=None),
        ).start()

        self.mockOsPathExists = patch.object(
            os.path,
            "exists",
            MagicMock(return_value=True),
        ).start()

        self.mockODPRGetPackageVersions = patch.object(
            OneDockerPackageRepository,
            "get_package_versions",
            MagicMock(return_value=[self.version]),
        ).start()
        self.mockODPRGetPackageInfo = patch.object(
            OneDockerPackageRepository,
            "get_package_info",
            MagicMock(return_value=self.package_info),
        ).start()

        self.mockContainerService = patch.object(
            AWSContainerService,
            "__init__",
            MagicMock(return_value=None),
        ).start()
        self.mockLogService = patch.object(
            CloudWatchLogService,
            "__init__",
            MagicMock(return_value=None),
        ).start()

        self.addCleanup(patch.stopall)

    def _get_test_config_dict(self, command: Optional[str] = None) -> Dict[str, Any]:
        if not command:
            # return full config
            test_config_file_contents = """
            onedocker-cli:
                dependency:
                    StorageService:
                        class: fbpcp.service.storage_s3.S3StorageService
                        constructor:
                            region: "us-west-2"
                    ContainerService:
                        class: fbpcp.service.container_aws.AWSContainerService
                        constructor:
                            region: us-west-2
                            cluster: pl-cluster-test
                    LogService:
                        class: fbpcp.service.log_cloudwatch.CloudWatchLogService
                        constructor:
                            region: us-west-2
                            log_group: /ecs/onedocker-cli-test
                setting:
                    repository_path: "https://onedocker-checksum-test.s3.us-west-2.amazonaws.com/binaries/"
                    task_definition: onedocker-cli-test:2#onedocker-cli-test
            """
        elif command in ["upload", "archive", "show"]:
            test_config_file_contents = """
            onedocker-cli:
                dependency:
                    StorageService:
                        class: fbpcp.service.storage_s3.S3StorageService
                        constructor:
                            region: "us-west-2"
                setting:
                    repository_path: "https://onedocker-checksum-test.s3.us-west-2.amazonaws.com/binaries/"
            """
        elif command == "test":
            test_config_file_contents = """
            onedocker-cli:
                dependency:
                    StorageService:
                        class: fbpcp.service.storage_s3.S3StorageService
                        constructor:
                            region: "us-west-2"
                    ContainerService:
                        class: fbpcp.service.container_aws.AWSContainerService
                        constructor:
                            region: us-west-2
                            cluster: pl-cluster-test
                    LogService:
                        class: fbpcp.service.log_cloudwatch.CloudWatchLogService
                        constructor:
                            region: us-west-2
                            log_group: /ecs/onedocker-cli-test
                setting:
                    task_definition: onedocker-cli-test:2#onedocker-cli-test
            """
        elif command == "stop":
            test_config_file_contents = """
            onedocker-cli:
                dependency:
                    StorageService:
                        class: fbpcp.service.storage_s3.S3StorageService
                        constructor:
                            region: "us-west-2"
                    ContainerService:
                        class: fbpcp.service.container_aws.AWSContainerService
                        constructor:
                            region: us-west-2
                            cluster: pl-cluster-test
                setting:
                    task_definition: onedocker-cli-test:2#onedocker-cli-test
            """
        else:
            raise ValueError("Invalid command.")

        return yaml.load(test_config_file_contents, Loader=yaml.SafeLoader)

    def test_docopt_args_upload(self):
        # Arrange
        doc = __onedocker_cli_doc__

        expected_args = self.base_args
        expected_args.update(
            {
                "upload": True,
                "--package_name": self.package_name,
                "--version": self.version,
                "--package_path": self.package_path,
                "--config": self.config_file,
            }
        )

        # Act
        args = docopt(
            doc,
            [
                "upload",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--package_path=" + self.package_path,
                "--version=" + self.version,
            ],
        )

        # Assert
        self.assertDictEqual(expected_args, args)

    def test_docopt_args_archive(self):
        # Arrange
        doc = __onedocker_cli_doc__

        expected_args = self.base_args
        expected_args.update(
            {
                "archive": True,
                "--package_name": self.package_name,
                "--version": self.version,
                "--config": self.config_file,
            }
        )

        # Act
        args = docopt(
            doc,
            [
                "archive",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--version=" + self.version,
            ],
        )

        # Assert
        self.assertDictEqual(expected_args, args)

    def test_docopt_args_test(self):
        # Arrange
        doc = __onedocker_cli_doc__

        expected_args = self.base_args
        expected_args.update(
            {
                "test": True,
                "--config": self.config_file,
                "--package_name": self.package_name,
                "--cmd_args": self.cmd_args,
                "--timeout": self.timeout,
            }
        )

        # Act
        args = docopt(
            doc,
            [
                "test",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--cmd_args=" + self.cmd_args,
                "--timeout=" + self.timeout,
            ],
        )

        # Assert
        self.assertDictEqual(expected_args, args)

    def test_docopt_args_show(self):
        # Arrange
        doc = __onedocker_cli_doc__

        expected_args = self.base_args
        expected_args.update(
            {
                "show": True,
                "--config": self.config_file,
                "--package_name": self.package_name,
            }
        )

        # Act
        args = docopt(
            doc,
            [
                "show",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
            ],
        )

        # Assert
        self.assertDictEqual(expected_args, args)

    def test_docopt_args_stop(self):
        # Arrange
        doc = __onedocker_cli_doc__

        expected_args = self.base_args
        expected_args.update(
            {
                "stop": True,
                "--config": self.config_file,
                "--container": self.container,
            }
        )

        # Act
        args = docopt(
            doc,
            [
                "stop",
                "--config=" + self.config_file,
                "--container=" + self.container,
            ],
        )

        # Assert
        self.assertDictEqual(expected_args, args)

    @patch(
        "onedocker.repository.onedocker_repository_service.OneDockerRepositoryService._skip_version_validation_check",
        return_value=True,
    )
    def test_upload(self, mockRepoSvc):
        # Arrange & Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "upload",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--package_path=" + self.package_path,
                "--version=" + self.version,
            ],
        ):
            main()

        # Assert
        self.mockYamlLoad.assert_called_once()
        self.mockODPRUpload.assert_called_once_with(
            self.package_name, self.version, self.package_path
        )

    @patch(
        "onedocker.repository.onedocker_repository_service.OneDockerRepositoryService._skip_version_validation_check",
        return_value=True,
    )
    def test_upload_with_partial_config(self, mockRepoSvc):
        # Arrange
        partial_config_dict = self._get_test_config_dict("upload")
        mockYamlLoad = patch.object(
            util_yaml,
            "load",
            MagicMock(return_value=partial_config_dict),
        ).start()

        # Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "upload",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--package_path=" + self.package_path,
                "--version=" + self.version,
            ],
        ):
            main()

        # Assert
        mockYamlLoad.assert_called_once()
        self.mockODPRUpload.assert_called_once_with(
            self.package_name, self.version, self.package_path
        )

    def test_upload_with_partial_config_throw(self):
        # Arrange
        invalid_config_dict = self._get_test_config_dict("test")
        mockYamlLoad = patch.object(
            util_yaml,
            "load",
            MagicMock(return_value=invalid_config_dict),
        ).start()

        # Act
        with self.assertRaises(KeyError):
            with patch.object(
                sys,
                "argv",
                [
                    "onedocker-cli",
                    "upload",
                    "--config=" + self.config_file,
                    "--package_name=" + self.package_name,
                    "--package_path=" + self.package_path,
                    "--version=" + self.version,
                ],
            ):
                main()

            mockYamlLoad.assert_called_once()

    def test_upload_throw_without_version(self):
        # Arrange & Act
        with self.assertRaises(DocoptExit):
            with patch.object(
                sys,
                "argv",
                [
                    "onedocker-cli",
                    "upload",
                    "--config=" + self.config_file,
                    "--package_name=" + self.package_name,
                    "--package_path=" + self.package_path,
                ],
            ):
                main()

        # Assert
        self.mockYamlLoad.assert_not_called()
        self.mockODPRUpload.assert_not_called()

    def test_archive(self):
        # Arrange & Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "archive",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--version=" + self.version,
            ],
        ):
            main()

        # Assert
        self.mockYamlLoad.assert_called_once()
        self.mockODPRArchive.assert_called_once_with(self.package_name, self.version)

    @patch.object(CloudWatchLogService, "get_log_path")
    @patch.object(OneDockerService, "wait_for_pending_container")
    @patch.object(OneDockerService, "start_container")
    @patch.object(CloudWatchLogService, "fetch")
    @patch.object(AWSContainerService, "get_instance")
    def test_test(
        self,
        mockAWSContainerServiceGetInstance,
        mockCloudWatchLogServiceFetch,
        mockOnedockerServiceStartContainer,
        mockOnedockerServiceWaitForPendingContainer,
        mockCloudWatchLogServiceGetLogPath,
    ):
        # Arrange
        mockCloudWatchLogServiceGetLogPath.return_value = (
            "Clearly/Bogus/File/Path/Here/"
        )
        mockCloudWatchLogServiceFetch.return_value = []

        mockContainerInstance = MagicMock(instance_id=1)

        mockContainerInstance.status.side_effect = [
            ContainerInstanceStatus.STARTED,
            ContainerInstanceStatus.STARTED,
            ContainerInstanceStatus.COMPLETED,
        ]
        mockOnedockerServiceStartContainer.return_value = mockContainerInstance
        mockOnedockerServiceWaitForPendingContainer.return_value = mockContainerInstance
        mockAWSContainerServiceGetInstance.return_value = mockContainerInstance

        # Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "test",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--version=" + self.version,
                "--cmd_args=" + self.cmd_args,
            ],
        ):
            main()

        # Assert
        self.mockYamlLoad.assert_called_once()
        mockOnedockerServiceStartContainer.assert_called_once_with(
            package_name=self.package_name,
            version=self.version,
            cmd_args=self.cmd_args,
            timeout=18000,
        )
        mockCloudWatchLogServiceGetLogPath.assert_called_once_with(
            mockContainerInstance
        )

    @patch.object(CloudWatchLogService, "get_log_path")
    @patch.object(OneDockerService, "wait_for_pending_container")
    @patch.object(OneDockerService, "start_container")
    @patch.object(CloudWatchLogService, "fetch")
    @patch.object(AWSContainerService, "get_instance")
    def test_test_with_partial_config(
        self,
        mockAWSContainerServiceGetInstance,
        mockCloudWatchLogServiceFetch,
        mockOnedockerServiceStartContainer,
        mockOnedockerServiceWaitForPendingContainer,
        mockCloudWatchLogServiceGetLogPath,
    ):
        # Arrange
        config_dict = self._get_test_config_dict("test")
        mockYamlLoad = patch.object(
            util_yaml,
            "load",
            MagicMock(return_value=config_dict),
        ).start()
        mockCloudWatchLogServiceGetLogPath.return_value = (
            "Clearly/Bogus/File/Path/Here/"
        )
        mockCloudWatchLogServiceFetch.return_value = []

        mockContainerInstance = MagicMock(instance_id=1)

        mockContainerInstance.status.side_effect = [
            ContainerInstanceStatus.STARTED,
            ContainerInstanceStatus.STARTED,
            ContainerInstanceStatus.COMPLETED,
        ]
        mockOnedockerServiceStartContainer.return_value = mockContainerInstance
        mockOnedockerServiceWaitForPendingContainer.return_value = mockContainerInstance
        mockAWSContainerServiceGetInstance.return_value = mockContainerInstance

        # Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "test",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--version=" + self.version,
                "--cmd_args=" + self.cmd_args,
            ],
        ):
            main()

        # Assert
        mockYamlLoad.assert_called_once()
        mockOnedockerServiceStartContainer.assert_called_once_with(
            package_name=self.package_name,
            version=self.version,
            cmd_args=self.cmd_args,
            timeout=18000,
        )
        mockCloudWatchLogServiceGetLogPath.assert_called_once_with(
            mockContainerInstance
        )

    def test_test_with_partial_config_throw(
        self,
    ):
        # Arrange
        invalid_config_dict = self._get_test_config_dict("upload")
        mockYamlLoad = patch.object(
            util_yaml,
            "load",
            MagicMock(return_value=invalid_config_dict),
        ).start()

        # Act & Assert
        with self.assertRaises(KeyError):
            with patch.object(
                sys,
                "argv",
                [
                    "onedocker-cli",
                    "test",
                    "--config=" + self.config_file,
                    "--package_name=" + self.package_name,
                    "--version=" + self.version,
                    "--cmd_args=" + self.cmd_args,
                ],
            ):
                main()

            mockYamlLoad.assert_called_once()

    def test_show(self):
        # Arrange & Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "show",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--version=" + self.version,
            ],
        ):
            main()

        # Assert
        self.mockYamlLoad.assert_called_once()
        self.mockODPRGetPackageInfo.assert_called_once_with(
            self.package_name, self.version
        )

    def test_show_partial_config(self):
        # Arrange
        config_dict = self._get_test_config_dict("show")
        mockYamlLoad = patch.object(
            util_yaml,
            "load",
            MagicMock(return_value=config_dict),
        ).start()

        # Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "show",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--version=" + self.version,
            ],
        ):
            main()

        # Assert
        mockYamlLoad.assert_called_once()
        self.mockODPRGetPackageInfo.assert_called_once_with(
            self.package_name, self.version
        )

    def test_show_partial_config_throw(self):
        # Arrange
        _invalid_config_dict = self._get_test_config_dict("test")
        mockYamlLoad = patch.object(
            util_yaml,
            "load",
            MagicMock(return_value=_invalid_config_dict),
        ).start()

        # Act & Assert
        with self.assertRaises(KeyError):
            with patch.object(
                sys,
                "argv",
                [
                    "onedocker-cli",
                    "show",
                    "--config=" + self.config_file,
                    "--package_name=" + self.package_name,
                    "--version=" + self.version,
                ],
            ):
                main()

            mockYamlLoad.assert_called_once()
            self.mockODPRGetPackageInfo.assert_called_once_with(
                self.package_name, self.version
            )

    def test_show_no_version(self):
        # Arrange & Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "show",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
            ],
        ):
            main()

        # Assert
        self.mockYamlLoad.assert_called_once()
        self.mockODPRGetPackageVersions.assert_called_once_with(self.package_name)
        self.mockODPRGetPackageInfo.assert_called_once_with(
            self.package_name, self.version
        )

    @patch.object(OneDockerService, "stop_containers")
    def test_stop(self, mockOnedockerServiceStopContainers):
        # Arrange
        mockOnedockerServiceStopContainers.return_value = [None]

        # Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "stop",
                "--config=" + self.config_file,
                "--container=" + self.container,
            ],
        ):
            main()

        # Assert
        self.mockYamlLoad.assert_called_once()
        mockOnedockerServiceStopContainers.assert_called_once_with(
            [self.container],
        )

    @patch.object(OneDockerService, "stop_containers")
    def test_stop_with_partial_config(self, mockOnedockerServiceStopContainers):
        # Arrange
        config_dict = self._get_test_config_dict("stop")
        mockYamlLoad = patch.object(
            util_yaml,
            "load",
            MagicMock(return_value=config_dict),
        ).start()
        mockOnedockerServiceStopContainers.return_value = [None]

        # Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "stop",
                "--config=" + self.config_file,
                "--container=" + self.container,
            ],
        ):
            main()

        # Assert
        mockYamlLoad.assert_called_once()
        mockOnedockerServiceStopContainers.assert_called_once_with(
            [self.container],
        )

    def test_stop_with_partial_config_throw(self):
        # Arrange
        invalid_config_dict = self._get_test_config_dict("upload")
        mockYamlLoad = patch.object(
            util_yaml,
            "load",
            MagicMock(return_value=invalid_config_dict),
        ).start()

        # Act & Assert
        with self.assertRaises(KeyError):
            with patch.object(
                sys,
                "argv",
                [
                    "onedocker-cli",
                    "stop",
                    "--config=" + self.config_file,
                    "--container=" + self.container,
                ],
            ):
                main()

            mockYamlLoad.assert_called_once()
