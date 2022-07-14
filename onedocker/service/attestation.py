#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import json
import logging
from typing import Dict, List

from fbpcp.service.key_management import KeyManagementService

from onedocker.entity.attestation_error import AttestationError
from onedocker.entity.checksum_info import ChecksumInfo
from onedocker.entity.checksum_type import ChecksumType
from onedocker.service.checksum import LocalChecksumGenerator


class AttestationService:
    # Default checksum types
    DEFAULT_CHECKSUM_TYPES: List[ChecksumType] = [
        ChecksumType.MD5,
        ChecksumType.SHA256,
        ChecksumType.BLAKE2B,
    ]
    key_management_svc: KeyManagementService

    def __init__(self) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.checksum_generator = LocalChecksumGenerator()

    def _get_checksum_info(
        self,
        package_name: str,
        version: str,
        binary_path: str,
        checksum_types: List[ChecksumType] = DEFAULT_CHECKSUM_TYPES,
    ) -> ChecksumInfo:
        checksums: Dict[str, str] = self.checksum_generator.generate_checksums(
            binary_path=binary_path,
            checksum_algorithms=checksum_types,
        )

        return ChecksumInfo(
            package_name=package_name,
            version=version,
            checksums=checksums,
        )

    def track_binary(
        self,
        binary_path: str,
        package_name: str,
        version: str,
    ) -> str:
        """
        This Function generates then uploads checksums for passed in local binary

        Args:
            binary_path:    Local file path pointing to the package
            package_name:   Package Name to use when uploading file to checksum repository
            version:        Package Version to relay while uploading file to checksum repository

        Returns:
            formated_checksum_info:  A JSON formated file that contains all the checksum data for a file
        """
        # Generates checksums
        self.logger.info(f"Generating checksums for binary at {binary_path}")
        checksum_info = self._get_checksum_info(
            package_name=package_name,
            version=version,
            binary_path=binary_path,
        )
        formated_checksum_info = json.dumps(
            checksum_info.asdict(
                exclude={"signature"},
            ),
        )
        return formated_checksum_info

    def add_signature(self, formated_checksum_info: str, signature: str) -> str:
        checksum_dict = json.loads(formated_checksum_info)
        checksum_info = ChecksumInfo(**checksum_dict)
        checksum_info.signature = signature

        signed_checksum_info = json.dumps(
            checksum_info.asdict(),
        )
        return signed_checksum_info

    def attest_binary(
        self,
        binary_path: str,
        package_name: str,
        version: str,
        formated_checksum_info: str,
        checksum_algorithm: ChecksumType,
        pubkey_path: str,
    ) -> None:
        """
        This functions generates a checksum for a local file and then compares the generated value to what is stored in the checksum repository for the given package_name and version

        Args:
            binary_path:            Local file path pointing to the package
            package_name:           Package Name to use when downlading the checksum file from checksum repository
            version:                Package Version to relay while downloading the checksum file from checksum repository
            formated_checksum_info: String encoding of ChecksumInfo attaining to the JSON file format
            checksum_algorithm:     Checksum algorithm that should be used while attesting local binary
            pubkey_path:            Local file path pointing to a .pem file with the public key
        """
        checksum_info_dict = json.loads(formated_checksum_info)
        checksum_info = ChecksumInfo(**checksum_info_dict)

        # Verify signature
        checksum_info.verify_signature(pubkey_path)

        # Generates checksums
        self.logger.info(f"Generating checksums for binary at {binary_path}")
        binary_checksum_info = self._get_checksum_info(
            package_name=package_name,
            version=version,
            binary_path=binary_path,
            checksum_types=[checksum_algorithm],
        )

        if binary_checksum_info != checksum_info:
            raise AttestationError(
                "Downloaded binaries checksum information differs from uploaded package's checksum information"
            )
        self.logger.info("Binary successfully attested")
