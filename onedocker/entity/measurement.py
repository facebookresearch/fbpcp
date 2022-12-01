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
    # TODO These types are not finalized yet, only adding few to test the integration.
    # TODO will update/add later when developing measurement service
    MD5 = "MD5"
    SHA256 = "SHA256"

    @classmethod
    def has_member(cls, name: str) -> bool:
        return name in cls.__members__


@dataclass_json
@dataclass
class Measurement:
    key: MeasurementType
    value: str
