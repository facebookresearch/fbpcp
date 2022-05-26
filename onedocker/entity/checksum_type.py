#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from enum import Enum


class ChecksumType(Enum):
    MD5 = "MD5"
    SHA256 = "SHA256"
    BLAKE2B = "BLAKE2B"
