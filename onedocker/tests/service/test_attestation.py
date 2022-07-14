#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from json import dumps
from unittest.mock import MagicMock

from onedocker.entity.attestation_error import AttestationError
from onedocker.entity.checksum_info import ChecksumInfo
from onedocker.entity.checksum_type import ChecksumType
from onedocker.service.attestation import AttestationService


class TestAttestationService(unittest.TestCase):
    def setUp(self) -> None:
        # Globals varibales for tests
        self.test_package = {
            "binary_path": "/usr/bin/ls",
            "package_name": "ls",
            "version": "latest",
        }
        self.algorithms = list(ChecksumType)
        self.checksums = {
            k.name: f"valid_{k.name.lower()}_checksum_goes_here"
            for k in self.algorithms
        }
        self.attestation_service = AttestationService()
        self.file_contents = dumps(
            ChecksumInfo(
                package_name=self.test_package["package_name"],
                version=self.test_package["version"],
                checksums=self.checksums,
            ).asdict(),
            indent=4,
        )

        # Global mock objects for tests
        self.attestation_service.checksum_generator.generate_checksums = MagicMock(
            return_value=self.checksums
        )

    def test_track_binary_s3(self):
        # Arrange & Act
        formated_checksums = self.attestation_service.track_binary(
            binary_path=self.test_package["binary_path"],
            package_name=self.test_package["package_name"],
            version=self.test_package["version"],
        )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=self.algorithms,
        )
        self.assertEqual(formated_checksums, self.file_contents)

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
            package_name=self.test_package["package_name"],
            version=self.test_package["version"],
            formated_checksum_info=self.file_contents,
            checksum_algorithm=test_algorithm,
        )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=[test_algorithm],
        )

    def test_attest_binary_s3_nonmatching_algorithm(
        self,
    ):
        # Arrange
        checksum_key = list(self.checksums.keys())[-1]  # Should be blake2b
        test_algorithm = ChecksumType(checksum_key)

        modified_file_contents = self.file_contents.replace(
            checksum_key.upper(),
            "def_not_" + checksum_key.upper(),
        )  # Modify file contents to be missing checksum causing failure

        self.attestation_service.checksum_generator.generate_checksums.return_value = {
            checksum_key: self.checksums[checksum_key]
        }

        # Act
        with self.assertRaises(ValueError):
            self.attestation_service.attest_binary(
                binary_path=self.test_package["binary_path"],
                package_name=self.test_package["package_name"],
                version=self.test_package["version"],
                formated_checksum_info=modified_file_contents,
                checksum_algorithm=test_algorithm,
            )

        # Assert
        assert not self.attestation_service.checksum_generator.generate_checksums.called

    def test_attest_binary_s3_bad_name(
        self,
    ):
        # Arrange
        modified_file_contents = self.file_contents.replace(
            self.test_package["package_name"],
            f'def_not_{self.test_package["package_name"]}',
        )  # Modifying package name to cause failure

        checksum_key = list(self.checksums.keys())[0]  # Should be MD5
        test_algorithm = ChecksumType(checksum_key)

        # Act
        with self.assertRaises(AttestationError):
            self.attestation_service.attest_binary(
                binary_path=self.test_package["binary_path"],
                package_name=self.test_package["package_name"],
                version=self.test_package["version"],
                formated_checksum_info=modified_file_contents,
                checksum_algorithm=test_algorithm,
            )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=[test_algorithm],
        )

    def test_attest_binary_s3_bad_version(
        self,
    ):
        # Arrange
        modified_file_contents = self.file_contents.replace(
            self.test_package["version"],
            f'def_not_{self.test_package["version"]}',
        )  # Modifying package version to cause failure

        checksum_key = list(self.checksums.keys())[0]  # Should be MD5
        test_algorithm = ChecksumType(checksum_key)

        # Act
        with self.assertRaises(AttestationError):
            self.attestation_service.attest_binary(
                binary_path=self.test_package["binary_path"],
                package_name=self.test_package["package_name"],
                version=self.test_package["version"],
                formated_checksum_info=modified_file_contents,
                checksum_algorithm=test_algorithm,
            )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=[test_algorithm],
        )

    def test_attest_binary_s3_bad_checksum(
        self,
    ):
        # Arrange
        checksum_key = list(self.checksums.keys())[0]  # Should be MD5
        test_algorithm = ChecksumType(checksum_key)

        modified_file_contents = self.file_contents.replace(
            "valid_" + checksum_key.lower(), "invalid_" + checksum_key.lower()
        )  # Modifying md5 checksum to cause failure

        self.attestation_service.checksum_generator.generate_checksums.return_value = {
            checksum_key: self.checksums[checksum_key]
        }

        # Act
        with self.assertRaises(AttestationError):
            self.attestation_service.attest_binary(
                binary_path=self.test_package["binary_path"],
                package_name=self.test_package["package_name"],
                version=self.test_package["version"],
                formated_checksum_info=modified_file_contents,
                checksum_algorithm=test_algorithm,
            )

        # Assert
        self.attestation_service.checksum_generator.generate_checksums.assert_called_once_with(
            binary_path=self.test_package["binary_path"],
            checksum_algorithms=[test_algorithm],
        )
