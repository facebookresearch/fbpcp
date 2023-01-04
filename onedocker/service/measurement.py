#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import hashlib
from typing import Dict, List

from onedocker.entity.measurement import MeasurementType


class MeasurementService:
    def _get_content_bytes(self, file_path: str) -> bytes:
        with open(file_path, "rb") as file:
            content_bytes = file.read()
        return content_bytes

    def _generate_measurement(
        self,
        content_bytes: bytes,
        measurement_type: MeasurementType,
    ) -> str:
        hash_function = hashlib.new(measurement_type.value, content_bytes)
        return hash_function.hexdigest()

    def generate_measurements(
        self, measurement_types: List[MeasurementType], file_path: str
    ) -> Dict[MeasurementType, str]:
        content_bytes = self._get_content_bytes(file_path)
        measurements = {
            t: self._generate_measurement(content_bytes, t) for t in measurement_types
        }
        return measurements
