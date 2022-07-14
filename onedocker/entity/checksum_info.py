#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from onedocker.entity.checksum_type import ChecksumType


@dataclass
class ChecksumInfo:
    """
    This dataclass tracks a package's checksum info for attestation, to allow for easy comparision and tracking

    Fields:
        package_name:   String containing the package name
        version:        String containing the package version
        Checksums:      Dict that holds a pairing between a ChecksumType (Key) and the corresponding hash (Value)
    """

    package_name: str
    version: str
    checksums: Dict[str, str]

    def __post_init__(self) -> None:
        """
        This function ensures that all checksums all follow the correct style of a ChecksumType as key to avoid any issues from occuring with invalid types being passed
        """
        for checksum in self.checksums.copy().keys():
            checksum_type = ChecksumType(checksum)
            if checksum_type in self.checksums:
                self.checksums[checksum_type.name] = self.checksums[checksum]
                del self.checksums[checksum]

    def __eq__(self, other: ChecksumInfo) -> bool:
        """
        Compares two ChecksumInfo instances in previously decided order
        1.  Compares package_name
        2.  Compares version
        3.  Checks if overlaping checkum algorithms are present
        4.  Compares overlaping checksums
        """
        # Compare package details
        if self.package_name != other.package_name:
            return False
        if self.version != other.version:
            return False

        # Common algorithms used between both instances
        algorithms = set(self.checksums) & set(other.checksums)
        if len(algorithms) == 0:
            return False
        # Compare hexdigests of matching checksum algorithms
        for algorithm in algorithms:
            if self.checksums[algorithm] != other.checksums[algorithm]:
                return False
        return True

    def asdict(self) -> Dict[str, Any]:
        return self.__dict__
