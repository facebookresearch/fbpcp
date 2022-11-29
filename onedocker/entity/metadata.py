#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from typing import Any, Dict

from onedocker.entity.measurement import MeasurementType


@dataclass
class PackageMetadata:
    package_name: str
    version: str
    measurements: Dict[MeasurementType, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "package_name": self.package_name,
            "version": self.version,
            "measurements": {k.value: v for k, v in self.measurements.items()},
        }
