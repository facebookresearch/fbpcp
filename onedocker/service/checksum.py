#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from hashlib import new
from typing import Dict, List

from fbpcp.service.storage import PathType, StorageService
from onedocker.entity.checksum_type import ChecksumType


class LocalChecksumGenerator:
    def _get_checksum(
        self,
        contents: bytes,
        checksum_algorithm: str,
    ) -> Dict[str, str]:
        hash_function = new(checksum_algorithm.lower(), contents)
        return {checksum_algorithm: hash_function.hexdigest()}

    def _read_local_file(self, path: str) -> bytes:
        if StorageService.path_type(path) != PathType.Local:
            raise ValueError("Only supports local paths")

        try:
            with open(path, "rb") as file:
                contents = file.read()
        except FileNotFoundError:
            raise ValueError("Please ensure that file exists at path specified")
        return contents

    def generate_checksums(
        self,
        binary_path: str,
        checksum_algorithms: List[ChecksumType],
    ) -> Dict[str, str]:
        """
        Usage:
            generate_checksums("/usr/bin/ls")
        """
        if len(checksum_algorithms) == 0:
            raise ValueError("No hashing function(s) have been provided")
        encoded_contents = self._read_local_file(binary_path)
        checksums = {}
        for checksum_algorithm in checksum_algorithms:
            checksums.update(
                self._get_checksum(
                    encoded_contents,
                    checksum_algorithm.name,
                )
            )
        return checksums
