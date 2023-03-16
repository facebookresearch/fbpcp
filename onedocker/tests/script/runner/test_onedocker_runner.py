#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys
import unittest
from unittest.mock import MagicMock, patch

from docopt import docopt
from fbpcp.entity.certificate_request import CertificateRequest, KeyAlgorithm
from fbpcp.error.pcp import InvalidParameterError
from onedocker.entity.exit_code import ExitCode
from onedocker.repository.onedocker_repository_service import OneDockerRepositoryService
from onedocker.script.runner.onedocker_runner import (
    __doc__ as __onedocker_runner_doc__,
    main,
)


class TestOnedockerRunner(unittest.TestCase):
    def setUp(self):
        expected = CertificateRequest(
            key_algorithm=KeyAlgorithm.RSA,
            key_size=4096,
            passphrase="test",
            cert_folder=None,
            private_key_name=None,
            certificate_name=None,
            days_valid=5,
            country_name="US",
            state_or_province_name=None,
            locality_name=None,
            organization_name="Test Company",
            common_name=None,
            dns_name=None,
        )
        self.test_cert_params = expected.convert_to_cert_params()

    def test_simple_args(self):
        # Arrange
        doc = __onedocker_runner_doc__

        # Act
        args = docopt(doc, ["test_package", "--version=1.0"])

        # Assert
        self.assertEqual(args["<package_name>"], "test_package")
        self.assertEqual(args["--version"], "1.0")
        self.assertEqual(args["--repository_path"], None)
        self.assertEqual(args["--exe_path"], None)
        self.assertEqual(args["--exe_args"], None)
        self.assertEqual(args["--timeout"], None)
        self.assertEqual(args["--log_path"], None)
        self.assertEqual(args["--cert_params"], None)

    def test_complex_args(self):
        # Arrange
        doc = __onedocker_runner_doc__

        # Act
        args = docopt(
            doc,
            [
                "test_package_3",
                "--version=4.20",
                "--repository_path=/foo/bar/path",
                "--timeout=23",
                "--exe_args='-h'",
            ],
        )

        # Assert
        self.assertEqual(args["<package_name>"], "test_package_3")
        self.assertEqual(args["--version"], "4.20")
        self.assertEqual(args["--repository_path"], "/foo/bar/path")
        self.assertEqual(args["--exe_path"], None)
        self.assertEqual(args["--exe_args"], "'-h'")
        self.assertEqual(args["--timeout"], "23")
        self.assertEqual(args["--log_path"], None)
        self.assertEqual(args["--cert_params"], None)

    def test_main_no_args(self):
        # Arrange, Act & Assert
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(
            str(cm.exception),
            "Usage:\n    onedocker-runner <package_name> --version=<version> [options]",
        )

    def test_main_local(self):
        # Arrange
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "echo",
                "--version=latest",
                "--repository_path=local",
                "--exe_path=/usr/bin/",
                "--exe_args=test_message",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            self.assertEqual(cm.exception.code, ExitCode.SUCCESS)

    def test_main_local_timeout(self):
        # Arrange
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "sleep",
                "--version=latest",
                "--repository_path=local",
                "--exe_path=/usr/bin/",
                "--exe_args=2",
                "--timeout=1",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            self.assertEqual(cm.exception.code, ExitCode.TIMEOUT)

    @patch("onedocker.script.runner.onedocker_runner.run_cmd")
    def test_main_local_run_command_error(self, mock_run_cmd):
        # Arrange
        mock_run_cmd.side_effect = Exception("Failed to run command")
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "echo",
                "--version=latest",
                "--repository_path=local",
                "--exe_path=/usr/bin/",
                "--exe_args=test_message",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            self.assertEqual(cm.exception.code, ExitCode.ERROR)

    def test_main_local_executable_unavailable(self):
        # Arrange
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "foo",
                "--version=latest",
                "--repository_path=local",
                "--exe_path=/usr/bin/",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            self.assertEqual(cm.exception.code, ExitCode.SERVICE_UNAVAILABLE)

    @patch("onedocker.script.runner.onedocker_runner.run_cmd")
    def test_main_local_executable_failed(self, mock_run_cmd):
        # Arrange
        mock_run_cmd.return_value = 1
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "echo",
                "--version=latest",
                "--repository_path=local",
                "--exe_path=/usr/bin/",
                "--exe_args=test_message",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            mock_run_cmd.assert_called_once_with("/usr/bin/echo test_message", None)
            self.assertEqual(cm.exception.code, ExitCode.EXE_ERROR)

    @patch.object(OneDockerRepositoryService, "download")
    @patch("onedocker.script.runner.onedocker_runner.S3Path")
    @patch("onedocker.script.runner.onedocker_runner.S3StorageService")
    def test_main(
        self,
        mockS3StorageService,
        mockS3Path,
        mockOneDockerRepositoryServiceDownload,
    ):
        # Arrange
        mockS3Path.region = MagicMock(return_value="us_west_1")
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "echo",
                "--version=latest",
                "--repository_path=test_repo_path",
                "--timeout=1200",
                "--exe_path=/usr/bin/",
                "--exe_args=test_message",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            self.assertEqual(cm.exception.code, ExitCode.SUCCESS)
            mockOneDockerRepositoryServiceDownload.assert_called_once_with(
                "echo",
                "latest",
                "/usr/bin/echo",
            )

    def test_main_bad_cert(self):
        # Arrange
        wrong_cert_params = str(
            {
                "key_algorithm": KeyAlgorithm.RSA.value,
                "key_size": 4096,
                "organization_name": "Test Organization",
            }
        )
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "echo",
                "--version=latest",
                "--exe_path=/usr/bin/",
                "--exe_args=measurement/private_measurement/pcp/oss/onedocker/tests/script/runner",
                f"--cert_params={wrong_cert_params}",
            ],
        ):
            with patch(
                "os.getenv",
                side_effect=lambda x: getenv(x),
            ):
                # Act & Assert
                with self.assertRaises(InvalidParameterError):
                    main()

    def test_main_env(self):
        # Arrange & Act
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "echo",
                "--version=latest",
                '--exe_args="Test Message"',
                "--exe_path=/usr/bin/",
                "--repository_path=local",
            ],
        ):
            with patch("os.getenv", return_value=None):
                with self.assertRaises(SystemExit) as cm:
                    main()
                # Assert
                self.assertEqual(cm.exception.code, ExitCode.SUCCESS)

    @patch.object(OneDockerRepositoryService, "download")
    @patch("onedocker.script.runner.onedocker_runner.S3Path")
    @patch("onedocker.script.runner.onedocker_runner.S3StorageService")
    @patch("onedocker.script.runner.onedocker_runner._run_opawdl")
    def test_main_with_opa_enabled(
        self,
        mockOneDockerRunOPAWDL,
        MockS3StorageService,
        MockS3Path,
        mockOneDockerRepositoryServiceDownload,
    ):
        # Arrange
        test_opa_workflow_path = "/home/xyz.json"
        MockS3Path.region = MagicMock(return_value="us_west_1")
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "echo",
                "--version=latest",
                "--repository_path=test_repo_path",
                "--timeout=1200",
                "--exe_path=/usr/bin/",
                "--exe_args=test_message",
                f"--opa_workflow_path={test_opa_workflow_path}",
            ],
        ):
            # Act
            with self.assertRaises(SystemExit) as cm:
                main()
            # Assert
            self.assertEqual(cm.exception.code, 0)
            mockOneDockerRunOPAWDL.assert_called_once_with(test_opa_workflow_path)


def getenv(key):
    if key == "ONEDOCKER_REPOSITORY_PATH":
        return "test_repo_path"
    else:
        raise KeyError from None
