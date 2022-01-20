#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from fbpcp.service.storage import PathType, StorageService


class TestStorageService(unittest.TestCase):
    def test_path_type_s3(self) -> None:
        type_ = StorageService.path_type(
            "https://bucket-name.s3.Region.amazonaws.com/key-name"
        )
        self.assertEqual(type_, PathType.S3)

    def test_path_type_gcs(self) -> None:
        type_ = StorageService.path_type(
            "https://storage.cloud.google.com/bucket-name/key-name"
        )
        self.assertEqual(type_, PathType.GCS)

    def test_path_type_local(self) -> None:
        type_ = StorageService.path_type("/usr/file")
        self.assertEqual(type_, PathType.Local)
