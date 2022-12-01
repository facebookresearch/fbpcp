#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from typing import Any, Dict

from onedocker.entity.measurement import MeasurementType

from onedocker.entity.metadata import PackageMetadata


def map_dynamodbitem_to_packagemetadata(
    dynamodb_item: Dict[str, Any]
) -> PackageMetadata:
    measurements = {
        MeasurementType(key): value
        for key, value in dynamodb_item.get("measurements", {}).items()
    }
    return PackageMetadata(
        package_name=dynamodb_item.get("package_name"),
        version=dynamodb_item.get("version"),
        measurements=measurements,
    )
