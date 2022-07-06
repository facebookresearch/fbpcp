#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ChecksumInfo:
    package_name: str
    version: str
    checksums: Dict[str, str]

    def __eq__(self, other: ChecksumInfo) -> bool:
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
