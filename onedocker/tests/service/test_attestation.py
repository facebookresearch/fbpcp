#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from fbpcp.service.storage_s3 import S3StorageService
from onedocker.entity.checksum_type import ChecksumType
from onedocker.service.attestation import AttestationService
from onedocker.service.checksum import LocalChecksumGenerator


class TestAttestationService(unittest.TestCase):
    @patch.object(LocalChecksumGenerator, "generate_checksums")
    @patch.object(S3StorageService, "write")
    def test_track_binary_s3(
        self,
        mockS3StorageServiceWrite,
        mockLocalChecksumGeneratorGenerateChecksum,
    ):
        # Arrange
        repository_path = (
            "https://onedocker-runner-unittest-asacheti.s3.us-west-2.amazonaws.com/"
        )
        attestation_service = AttestationService(
            S3StorageService("us-west-2"),
            repository_path,
        )

        algorithms = [ChecksumType.MD5, ChecksumType.SHA256, ChecksumType.BLAKE2B]

        test_path = "/usr/bin/ls"
        test_package_name = "ls"
        test_version = "latest"

        checksums = {
            "MD5": "valid_md5_checksum_goes_here",
            "SHA256": "valid_sha256_checksum_goes_here",
            "BLAKE2B": "valid_blake2b_checksum_goes_here",
        }
        mockLocalChecksumGeneratorGenerateChecksum.return_value = checksums

        expected_file_contents = (
            "{\n"
            + '    "Package Name": "ls",\n'
            + '    "Package Version": "latest",\n'
            + '    "Checksums": {\n'
            + '        "MD5": "valid_md5_checksum_goes_here",\n'
            + '        "SHA256": "valid_sha256_checksum_goes_here",\n'
            + '        "BLAKE2B": "valid_blake2b_checksum_goes_here"\n'
            + "    }\n"
            + "}"
        )
        expected_file_path = f"{repository_path}ls/latest.json"

        # Act
        attestation_service.track_binary(
            binary_path=test_path,
            package_name=test_package_name,
            version=test_version,
        )

        # Assert
        mockLocalChecksumGeneratorGenerateChecksum.assert_called_once_with(
            binary_path=test_path,
            checksum_algorithms=algorithms,
        )
        mockS3StorageServiceWrite.assert_called_once_with(
            expected_file_path,
            expected_file_contents,
        )

    @patch.object(LocalChecksumGenerator, "generate_checksums")
    @patch.object(S3StorageService, "file_exists")
    @patch.object(S3StorageService, "read")
    def test_verify_binary_s3(
        self,
        mockS3StorageServiceRead,
        mockS3StorageServiceFileExists,
        mockLocalChecksumGeneratorGenerateChecksum,
    ):
        # Arrange
        file_contents = (
            "{\n"
            + '    "Package Name": "ls",\n'
            + '    "Package Version": "latest",\n'
            + '    "Checksums": {\n'
            + '        "MD5": "valid_md5_checksum_goes_here",\n'
            + '        "SHA256": "valid_sha256_checksum_goes_here"\n'
            + "    }\n}"
        )
        mockS3StorageServiceRead.return_value = file_contents
        mockS3StorageServiceFileExists.return_value = True

        checksums = {
            "MD5": "valid_md5_checksum_goes_here",
        }
        mockLocalChecksumGeneratorGenerateChecksum.return_value = checksums

        repository_path = (
            "https://onedocker-runner-unittest-asacheti.s3.us-west-2.amazonaws.com/"
        )
        attestation_service = AttestationService(
            S3StorageService("us-west-2"),
            repository_path,
        )

        test_path = "/usr/bin/ls"
        test_package_name = "ls"
        test_version = "latest"
        test_algorithm = ChecksumType.MD5
        expected_file_path = f"{repository_path}ls/latest.json"

        # Act
        attestation_service.verify_binary(
            binary_path=test_path,
            package_name=test_package_name,
            version=test_version,
            checksum_algorithm=test_algorithm,
        )

        # Assert
        mockLocalChecksumGeneratorGenerateChecksum.assert_called_once_with(
            binary_path=test_path,
            checksum_algorithms=[test_algorithm],
        )
        mockS3StorageServiceRead.assert_called_once_with(
            expected_file_path,
        )
        mockS3StorageServiceFileExists.assert_called_once_with(
            expected_file_path,
        )

    @patch.object(LocalChecksumGenerator, "generate_checksums")
    @patch.object(S3StorageService, "file_exists")
    @patch.object(S3StorageService, "read")
    def test_verify_binary_s3_nonmatching_algorithm(
        self,
        MockS3StorageServiceRead,
        MockS3StorageServiceFileExists,
        MockLocalChecksumGeneratorGenerateChecksum,
    ):
        # Arrange
        file_contents = (
            "{\n"
            + '    "Package Name": "ls",\n'
            + '    "Package Version": "latest",\n'
            + '    "Checksums": {\n'
            + '        "MD5": "valid_md5_checksum_goes_here",\n'
            + '        "SHA256": "valid_sha256_checksum_goes_here"\n'
            + "    }\n}"
        )
        MockS3StorageServiceRead.return_value = file_contents
        MockS3StorageServiceFileExists.return_value = True

        checksums = {
            "BLAKE2B": "valid_blake2b_checksum_goes_here",
        }
        MockLocalChecksumGeneratorGenerateChecksum.return_value = checksums

        repository_path = (
            "https://onedocker-runner-unittest-asacheti.s3.us-west-2.amazonaws.com/"
        )
        attestation_service = AttestationService(
            S3StorageService("us-west-2"),
            repository_path,
        )

        test_path = "/usr/bin/ls"
        test_package_name = "ls"
        test_version = "latest"
        test_algorithm = ChecksumType.BLAKE2B
        expected_file_path = f"{repository_path}ls/latest.json"

        # Act
        with self.assertRaises(ValueError):
            attestation_service.verify_binary(
                binary_path=test_path,
                package_name=test_package_name,
                version=test_version,
                checksum_algorithm=test_algorithm,
            )

        # Assert
        MockLocalChecksumGeneratorGenerateChecksum.assert_called_once_with(
            binary_path=test_path,
            checksum_algorithms=[test_algorithm],
        )
        MockS3StorageServiceRead.assert_called_once_with(
            expected_file_path,
        )
        MockS3StorageServiceFileExists.assert_called_once_with(
            expected_file_path,
        )

    @patch.object(LocalChecksumGenerator, "generate_checksums")
    @patch.object(S3StorageService, "file_exists")
    @patch.object(S3StorageService, "read")
    def test_verify_binary_s3_bad_name(
        self,
        MockS3StorageServiceRead,
        MockS3StorageServiceFileExists,
        MockLocalChecksumGeneratorGenerateChecksum,
    ):
        # Arrange
        file_contents = (
            "{\n"
            + '    "Package Name": "badls",\n'
            + '    "Package Version": "latest",\n'
            + '    "Checksums": {\n'
            + '        "MD5": "valid_md5_checksum_goes_here",\n'
            + '        "SHA256": "valid_sha256_checksum_goes_here"\n'
            + "    }\n}"
        )
        MockS3StorageServiceRead.return_value = file_contents
        MockS3StorageServiceFileExists.return_value = True

        repository_path = (
            "https://onedocker-runner-unittest-asacheti.s3.us-west-2.amazonaws.com/"
        )
        attestation_service = AttestationService(
            S3StorageService("us-west-2"),
            repository_path,
        )

        test_path = "/usr/bin/ls"
        test_package_name = "ls"
        test_version = "latest"
        test_algorithm = ChecksumType.MD5
        expected_file_path = f"{repository_path}ls/latest.json"

        # Act
        with self.assertRaises(ValueError):
            attestation_service.verify_binary(
                binary_path=test_path,
                package_name=test_package_name,
                version=test_version,
                checksum_algorithm=test_algorithm,
            )

        # Assert
        assert not MockLocalChecksumGeneratorGenerateChecksum.called
        MockS3StorageServiceRead.assert_called_once_with(
            expected_file_path,
        )
        MockS3StorageServiceFileExists.assert_called_once_with(
            expected_file_path,
        )
