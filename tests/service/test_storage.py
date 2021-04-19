#!/usr/bin/env python3

import unittest

from service.storage import PathType, StorageService


class TestStorageService(unittest.TestCase):
    def test_path_type_s3(self):
        type_ = StorageService.path_type(
            "https://bucket-name.s3.Region.amazonaws.com/key-name"
        )
        self.assertEqual(type_, PathType.S3)

    def test_path_type_local(self):
        type_ = StorageService.path_type("/usr/file")
        self.assertEqual(type_, PathType.Local)
