#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from typing import Any, Dict

from onedocker.entity.checksum_type import ChecksumType


@dataclass
class ChecksumInfo:
    """
    This dataclass tracks a package's checksum info for attestation, to allow for easy comparision and tracking

    Fields:
        package_name:   String containting the package's name
        version:        String containting the package's version
        Checksums:      Dict that holds a pairing between a ChecksumType and the corresponding hash for that ChecksumType
    """

    package_name: str
    version: str
    checksums: Dict[ChecksumType, str]

    def __post_init__(self) -> None:
        """
        This function ensures that correct types are used after initializing dataclass to avoid ChecksumType misses later in use

        """
        for checksum in self.checksums.copy().keys():
            checksum_type = ChecksumType(checksum)
            if checksum_type in self.checksums:
                self.checksums[checksum_type.name] = self.checksums[checksum]
                del self.checksums[checksum]

    def asdict(self) -> Dict[str, Any]:
        return self.__dict__
