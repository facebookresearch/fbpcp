#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass

from enum import Enum

from dataclasses_json import dataclass_json


class MeasurementType(Enum):
    sha256 = "sha256"
    sha512 = "sha512"

    @classmethod
    def has_member(cls, name: str) -> bool:
        return name in cls.__members__


@dataclass_json
@dataclass
class Measurement:
    key: MeasurementType
    value: str
