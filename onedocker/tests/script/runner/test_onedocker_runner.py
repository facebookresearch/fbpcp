#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import signal
import sys
import unittest
from unittest.mock import patch

from docopt import docopt
from fbpcp.entity.certificate_request import CertificateRequest, KeyAlgorithm
from fbpcp.error.pcp import InvalidParameterError
from onedocker.common.core_dump_handler_aws import AWSCoreDumpHandler
from onedocker.entity.checksum_type import ChecksumType
from onedocker.repository.onedocker_checksum import OneDockerChecksumRepository
from onedocker.repository.onedocker_package import OneDockerPackageRepository
from onedocker.script.runner.onedocker_runner import (
    __doc__ as __onedocker_runner_doc__,
    main,
)
from onedocker.service.attestation import AttestationService
from onedocker.service.certificate_self_signed import SelfSignedCertificateService


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
            self.assertEqual(cm.exception.code, 0)

    def test_main_local_timeout(self):
        # Arrange
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "nano",
                "--version=latest",
                "--repository_path=local",
                "--exe_path=test.py",
                "--timeout=1",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            self.assertEqual(cm.exception.code, 1)

    @patch.object(AttestationService, "attest_binary")
    @patch.object(OneDockerChecksumRepository, "read")
    @patch.object(OneDockerPackageRepository, "download")
    def test_main(
        self,
        mockOneDockerPackageRepositoryDownload,
        mockOneDockerChecksumRepositoryRead,
        mockAttestationServiceAttestBinary,
    ):
        # Arrange
        mockAttestationServiceAttestBinary.return_value = None
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "echo",
                "--version=latest",
                "--repository_path=https://onedocker-runner-unittest-asacheti.s3.us-west-2.amazonaws.com/",
                "--timeout=1200",
                "--exe_path=/usr/bin/",
                "--exe_args=test_message",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            self.assertEqual(cm.exception.code, 0)
            mockOneDockerPackageRepositoryDownload.assert_called_once_with(
                "echo",
                "latest",
                "/usr/bin/echo",
            )

    @patch.object(SelfSignedCertificateService, "generate_certificate")
    def test_main_good_cert(
        self,
        mockSelfSignedCertificateServiceGenerateCertificate,
    ):
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
                f"--cert_params={self.test_cert_params}",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            self.assertEqual(cm.exception.code, 0)
            mockSelfSignedCertificateServiceGenerateCertificate.assert_called_once_with()

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
            with patch(
                "os.getenv",
                side_effect=lambda x: getenv(x),
            ):
                with self.assertRaises(SystemExit) as cm:
                    main()
                # Assert
                self.assertEqual(cm.exception.code, 0)

    @patch.object(AttestationService, "attest_binary")
    @patch.object(OneDockerChecksumRepository, "read")
    @patch.object(OneDockerPackageRepository, "download")
    def test_main_checksum(
        self,
        mockOneDockerPackageRepositoryDownload,
        mockOneDockerChecksumRepositoryRead,
        mockAttestationServiceAttestBinary,
    ):
        # Arrange
        mockAttestationServiceAttestBinary.return_value = None
        mockOneDockerChecksumRepositoryRead.return_value = "checksum_info_goes_here"
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "ls",
                "--version=latest",
                "--repository_path=https://onedocker-runner-unittest-asacheti.s3.us-west-2.amazonaws.com/",
                "--timeout=1200",
                "--exe_path=/usr/bin/",
                "--exe_args=-l",
                "--checksum_repository_path=https://one-docker-checksum-repository-prod.s3.us-west-2.amazonaws.com/",
                "--checksum_type=BLAKE2B",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            self.assertEqual(cm.exception.code, 0)
            mockOneDockerPackageRepositoryDownload.assert_called_once_with(
                "ls",
                "latest",
                "/usr/bin/ls",
            )
        mockAttestationServiceAttestBinary.assert_called_once_with(
            binary_path="/usr/bin/ls",
            package_name="ls",
            version="latest",
            formated_checksum_info="checksum_info_goes_here",
            checksum_algorithm=ChecksumType.BLAKE2B,
        )
        mockOneDockerChecksumRepositoryRead.assert_called_once_with(
            "ls",
            "latest",
        )

    @patch.object(AttestationService, "attest_binary")
    @patch.object(OneDockerChecksumRepository, "read")
    @patch.object(OneDockerPackageRepository, "download")
    def test_main_checksum_default_type(
        self,
        mockOneDockerPackageRepositoryDownload,
        mockOneDockerChecksumRepositoryRead,
        mockAttestationServiceAttestBinary,
    ):
        # Arrange
        mockAttestationServiceAttestBinary.return_value = None
        mockOneDockerChecksumRepositoryRead.return_value = "checksum_info_goes_here"
        with patch.object(
            sys,
            "argv",
            [
                "onedocker-runner",
                "ls",
                "--version=latest",
                "--repository_path=https://onedocker-runner-unittest-asacheti.s3.us-west-2.amazonaws.com/",
                "--timeout=1200",
                "--exe_path=/usr/bin/",
                "--exe_args=-l",
                "--checksum_repository_path=https://one-docker-checksum-repository-prod.s3.us-west-2.amazonaws.com/",
            ],
        ):
            with self.assertRaises(SystemExit) as cm:
                # Act
                main()

            # Assert
            self.assertEqual(cm.exception.code, 0)
            mockOneDockerPackageRepositoryDownload.assert_called_once_with(
                "ls",
                "latest",
                "/usr/bin/ls",
            )
        mockAttestationServiceAttestBinary.assert_called_once_with(
            binary_path="/usr/bin/ls",
            package_name="ls",
            version="latest",
            formated_checksum_info="checksum_info_goes_here",
            checksum_algorithm=ChecksumType.SHA256,
        )
        mockOneDockerChecksumRepositoryRead.assert_called_once_with(
            "ls",
            "latest",
        )

    @patch("onedocker.script.runner.onedocker_runner.run_cmd")
    @patch.object(AWSCoreDumpHandler, "locate_core_dump_file")
    @patch.object(AWSCoreDumpHandler, "upload_core_dump_file")
    def test_main_core_dump(
        self, mockUploadCoreDumpFile, mockLocateCoreDumpFile, mockRunCMD
    ):
        # Arrange & Act
        error_code = 128 + signal.SIGSEGV
        mockRunCMD.return_value = error_code
        core_dump_file = "core_dump.txt"
        mockLocateCoreDumpFile.return_value = core_dump_file

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
            with patch(
                "os.getenv",
                side_effect=lambda x: getenv(x),
            ):
                with self.assertRaises(SystemExit) as cm:
                    main()
                # Assert
                self.assertEqual(cm.exception.code, error_code)
        mockLocateCoreDumpFile.assert_called_once()
        mockUploadCoreDumpFile.assert_called_once_with(
            core_dump_file, getenv("CORE_DUMP_REPOSITORY_PATH")
        )


def getenv(key):
    if key == "ONEDOCKER_REPOSITORY_PATH":
        return "https://onedocker-package-repo.s3.us-west-2.amazonaws.com/"
    elif key == "ONEDOCKER_CHECKSUM_REPOSITORY_PATH":
        return "https://onedocker-checksum-repo.s3.us-west-2.amazonaws.com/checksums/"
    elif key == "CORE_DUMP_REPOSITORY_PATH":
        return "https://onedocker-core-dump.s3.us-west-2.amazonaws.com/checksums/"
    else:
        return None
