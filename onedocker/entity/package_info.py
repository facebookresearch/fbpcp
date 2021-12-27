#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass


@dataclass
class PackageInfo:
    package_name: str
    version: str
    last_modified: str
    package_size: int
