#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from json import dumps
from unittest.mock import MagicMock, patch

from fbpcp.service.storage_s3 import S3StorageService
from onedocker.entity.attestation_error import AttestationError
from onedocker.entity.checksum_info import ChecksumInfo
from onedocker.entity.checksum_type import ChecksumType
from onedocker.service.attestation import AttestationService


class TestAttestationService(unittest.TestCase):
    def setUp(self) -> None:
        # Globals varibales for tests
        self.repository_path = (
            "https://onedocker-runner-unittest-asacheti.s3.us-west-2.amazonaws.com/"
        )
        checksum_path = f"{self.repository_path}ls/latest.json"
        self.test_package = {
            "binary_path": "/usr/bin/ls",
            "checksum_path": checksum_path,
            "name": "ls",
            "version": "latest",
        }
        self.algorithms = list(ChecksumType)
        self.checksums = {
            k.name: f"valid_{k.name.lower()}_checksum_goes_here"
            for k in self.algorithms
        }
        self.attestation_service = AttestationService(
            S3StorageService("us-west-2"),
            self.repository_path,
        )
        self.file_contents = dumps(
            ChecksumInfo(
                package_name=self.test_package["name"],
                version=self.test_package["version"],
                checksums=self.checksums,
            ).asdict(),
            indent=4,
        )

        # Global mock objects for tests
        self.attestation_service.checksum_generator.generate_checksums = MagicMock(
            return_value=self.checksums
        )
        self.attestation_service.storage_svc.read = MagicMock(
            return_value=self.file_contents
        )
        self.attestation_service.storage_svc.file_exists = MagicMock(return_value=True)

    @patch.object(S3StorageService, "write")
    def test_track_binary_s3(
        self,
        mockS3StorageServiceWrite,
    ):
        # Arrange & Act
        self.attestation_service.track_binary(
            binary_path=self.test_package["binary_path"],
            package_name=self.test_package["name"],
            version=self.test_package["version"],
        )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=self.algorithms,
        )
        mockS3StorageServiceWrite.assert_called_once_with(
            self.test_package["checksum_path"],
            self.file_contents,
        )

    def test_attest_binary_s3(
        self,
    ):
        # Arrange
        checksum_key = list(self.checksums.keys())[0]  # Should be MD5
        test_algorithm = ChecksumType(checksum_key)

        self.attestation_service.checksum_generator.generate_checksums.return_value = {
            checksum_key: self.checksums[checksum_key]
        }

        # Act
        self.attestation_service.attest_binary(
            binary_path=self.test_package["binary_path"],
            package_name=self.test_package["name"],
            version=self.test_package["version"],
            checksum_algorithm=test_algorithm,
        )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=[test_algorithm],
        )
        self.attestation_service.storage_svc.read.assert_called_once_with(
            self.test_package["checksum_path"],
        )
        self.attestation_service.storage_svc.file_exists.assert_called_once_with(
            self.test_package["checksum_path"],
        )

    def test_attest_binary_s3_nonmatching_algorithm(
        self,
    ):
        # Arrange
        checksum_key = list(self.checksums.keys())[-1]  # Should be blake2b
        test_algorithm = ChecksumType(checksum_key)

        self.attestation_service.storage_svc.read.return_value = (
            self.file_contents.replace(
                checksum_key.upper(),
                "def_not_" + checksum_key.upper(),
            )
        )  # Modify file contents to be missing checksum causing failure

        self.attestation_service.checksum_generator.generate_checksums.return_value = {
            checksum_key: self.checksums[checksum_key]
        }

        # Act
        with self.assertRaises(AttestationError):
            self.attestation_service.attest_binary(
                binary_path=self.test_package["binary_path"],
                package_name=self.test_package["name"],
                version=self.test_package["version"],
                checksum_algorithm=test_algorithm,
            )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=[test_algorithm],
        )
        self.attestation_service.storage_svc.read.assert_called_once_with(
            self.test_package["checksum_path"],
        )
        self.attestation_service.storage_svc.file_exists.assert_called_once_with(
            self.test_package["checksum_path"],
        )

    def test_attest_binary_s3_bad_name(
        self,
    ):
        # Arrange
        self.attestation_service.storage_svc.read.return_value = (
            self.file_contents.replace(
                self.test_package["name"],
                f'def_not_{self.test_package["name"]}',
            )
        )  # Modifying package name to cause failure

        checksum_key = list(self.checksums.keys())[0]  # Should be MD5
        test_algorithm = ChecksumType(checksum_key)

        # Act
        with self.assertRaises(AttestationError):
            self.attestation_service.attest_binary(
                binary_path=self.test_package["binary_path"],
                package_name=self.test_package["name"],
                version=self.test_package["version"],
                checksum_algorithm=test_algorithm,
            )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=[test_algorithm],
        )
        self.attestation_service.storage_svc.read.assert_called_once_with(
            self.test_package["checksum_path"],
        )
        self.attestation_service.storage_svc.file_exists.assert_called_once_with(
            self.test_package["checksum_path"],
        )

    def test_attest_binary_s3_bad_version(
        self,
    ):
        # Arrange
        self.attestation_service.storage_svc.read.return_value = (
            self.file_contents.replace(
                self.test_package["version"],
                f'def_not_{self.test_package["version"]}',
            )
        )  # Modifying package version to cause failure

        checksum_key = list(self.checksums.keys())[0]  # Should be MD5
        test_algorithm = ChecksumType(checksum_key)

        # Act
        with self.assertRaises(AttestationError):
            self.attestation_service.attest_binary(
                binary_path=self.test_package["binary_path"],
                package_name=self.test_package["name"],
                version=self.test_package["version"],
                checksum_algorithm=test_algorithm,
            )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=[test_algorithm],
        )
        self.attestation_service.storage_svc.read.assert_called_once_with(
            self.test_package["checksum_path"],
        )
        self.attestation_service.storage_svc.file_exists.assert_called_once_with(
            self.test_package["checksum_path"],
        )

    def test_attest_binary_s3_bad_checksum(
        self,
    ):
        # Arrange
        checksum_key = list(self.checksums.keys())[0]  # Should be MD5
        test_algorithm = ChecksumType(checksum_key)

        self.attestation_service.storage_svc.read.return_value = (
            self.file_contents.replace(
                "valid_" + checksum_key.lower(), "invalid_" + checksum_key.lower()
            )
        )  # Modifying md5 checksum to cause failure

        self.attestation_service.checksum_generator.generate_checksums.return_value = {
            checksum_key: self.checksums[checksum_key]
        }

        # Act
        with self.assertRaises(AttestationError):
            self.attestation_service.attest_binary(
                binary_path=self.test_package["binary_path"],
                package_name=self.test_package["name"],
                version=self.test_package["version"],
                checksum_algorithm=test_algorithm,
            )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=[test_algorithm],
        )
        self.attestation_service.storage_svc.read.assert_called_once_with(
            self.test_package["checksum_path"],
        )
        self.attestation_service.storage_svc.file_exists.assert_called_once_with(
            self.test_package["checksum_path"],
        )
