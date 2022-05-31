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
    def test_upload_checksum_s3(
        self, MockS3StorageServiceWrite, MockLocalChecksumGeneratorGenerateChecksum
    ):
        # Arrange
        repository_path = (
            "https://onedocker-runner-unittest-asacheti.s3.us-west-2.amazonaws.com/"
        )
        attestation_service = AttestationService(
            S3StorageService("us-west-2"),
            repository_path,
        )

        algorithms = [ChecksumType.MD5, ChecksumType.SHA256]

        test_path = "/usr/bin/ls"
        test_package_name = "ls"
        test_version = "latest"

        MockLocalChecksumGeneratorGenerateChecksum.return_value = {
            "MD5": "valid_md5_checksum_goes_here",
            "SHA256": "valid_sha256_checksum_goes_here",
        }

        expected_file_contents = (
            "{\n"
            + '    "Package Name": "ls",\n'
            + '    "Package Version": "latest",\n'
            + '    "Checksums": {\n'
            + '        "MD5": "valid_md5_checksum_goes_here",\n'
            + '        "SHA256": "valid_sha256_checksum_goes_here"\n'
            + "    }\n}"
        )
        expected_file_path = f"{repository_path}ls/latest.json"

        # Act
        attestation_service.upload_checksum(
            path_to_binary=test_path,
            package_name=test_package_name,
            version=test_version,
            checksum_algorithms=algorithms,
        )

        # Assert
        MockLocalChecksumGeneratorGenerateChecksum.assert_called_once_with(
            path_to_binary=test_path,
            checksum_algorithms=algorithms,
        )
        MockS3StorageServiceWrite.assert_called_once_with(
            expected_file_path,
            expected_file_contents,
        )
