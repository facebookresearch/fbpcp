#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import yaml
from docopt import docopt
from fbpcp.entity.container_instance import ContainerInstanceStatus
from fbpcp.service.container_aws import AWSContainerService
from fbpcp.service.log_cloudwatch import CloudWatchLogService
from fbpcp.service.onedocker import OneDockerService
from fbpcp.util import yaml as util_yaml
from onedocker.entity.package_info import PackageInfo
from onedocker.repository.onedocker_checksum import OneDockerChecksumRepository
from onedocker.repository.onedocker_package import OneDockerPackageRepository
from onedocker.script.cli.onedocker_cli import __doc__ as __onedocker_cli_doc__, main
from onedocker.service.attestation import AttestationService


class TestOnedockerCli(unittest.TestCase):
    def setUp(self):
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
                    checksum_repository_path: "https://onedocker-checksum-test.s3.us-west-2.amazonaws.com/checksums/"
                    task_definition: onedocker-cli-test:2#onedocker-cli-test
            """
        self.test_config_dict = yaml.load(
            test_config_file_contents, Loader=yaml.SafeLoader
        )

        self.package_name = "foo"
        self.package_dir = "test/bar/"
        self.version = "baz"
        self.config_file = "test_config_file.yml"
        self.timeout = "100"
        self.cmd_args = "-h"
        self.container = "secret_container"
        self.checksums = "formatted_checksums_go_here"

        self.package_info = PackageInfo(
            package_name=self.package_name,
            version=self.version,
            last_modified="Sun Jan 01 01:01:05 2022",
            package_size=1048576,
        )

        self.base_args = {
            "upload": False,
            "test": False,
            "show": False,
            "stop": False,
            "--help": False,
            "--verbose": False,
            "--enable_attestation": False,
            "--package_name": None,
            "--version": None,
            "--package_dir": None,
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

        self.mockOsPathExists = patch.object(
            os.path,
            "exists",
            MagicMock(return_value=True),
        ).start()

        self.mockODPRUpload = patch.object(
            OneDockerPackageRepository,
            "upload",
            MagicMock(return_value=None),
        ).start()
        self.mockODCRWrite = patch.object(
            OneDockerChecksumRepository,
            "write",
            MagicMock(return_value=None),
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

        self.mockAttestationServiceTrackBinary = patch.object(
            AttestationService,
            "track_binary",
            MagicMock(return_value=self.checksums),
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

    def test_docopt_args_upload(self):
        # Arrange
        doc = __onedocker_cli_doc__

        expected_args = self.base_args
        expected_args.update(
            {
                "upload": True,
                "--enable_attestation": True,
                "--package_name": self.package_name,
                "--version": self.version,
                "--package_dir": self.package_dir,
                "--config": self.config_file,
            }
        )

        # Act
        args = docopt(
            doc,
            [
                "upload",
                "--enable_attestation",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--package_dir=" + self.package_dir,
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

    def test_upload(self):
        # Arrange & Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "upload",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--package_dir=" + self.package_dir,
                "--version=" + self.version,
            ],
        ):
            main()

        # Assert
        self.mockYamlLoad.assert_called_once()
        self.mockODPRUpload.assert_called_once_with(
            self.package_name, self.version, self.package_dir
        )

    def test_upload_attestation_service(self):
        # Arrange & Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-cli",
                "upload",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--package_dir=" + self.package_dir,
                "--version=" + self.version,
                "--enable_attestation",
            ],
        ):
            main()

        # Assert
        self.mockYamlLoad.assert_called_once()
        self.mockODCRWrite.assert_called_once_with(
            package_name=self.package_name,
            version=self.version,
            checksum_data=self.checksums,
        )
        self.mockODPRUpload.assert_called_once_with(
            self.package_name, self.version, self.package_dir
        )
        self.mockAttestationServiceTrackBinary.assert_called_once_with(
            binary_path=self.package_dir,
            package_name=self.package_name,
            version=self.version,
        )

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
