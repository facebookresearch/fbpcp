#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import unittest
from unittest.mock import call, MagicMock, patch

from onedocker.service.storage_s3 import S3StorageService


class TestS3StorageService(unittest.TestCase):
    LOCAL_FILE = "/usr/test_file"
    LOCAL_FOLDER = "/foo"
    S3_FILE = "https://bucket.s3.Region.amazonaws.com/test_file"
    S3_FILE_COPY = "https://bucket.s3.Region.amazonaws.com/test_file_copy"
    S3_FOLDER = "https://bucket.s3.Region.amazonaws.com/test_folder/"
    S3_FOLDER_COPY = "https://bucket.s3.Region.amazonaws.com/test_folder_copy/"
    S3_FILE_WITH_SUBFOLDER = (
        "https://bucket.s3.Region.amazonaws.com/test_folder/test_file"
    )
    """
    The layout of LOCAL_DIR:
    /foo/
    ├── bar/
    └── baz/
        ├── a
        └── b
    """
    LOCAL_DIR = [
        ("/foo", ("bar",), ("baz",)),
        ("/foo/baz", (), ("a", "b")),
    ]

    S3_DIR = [
        "test_folder/bar/",
        "test_folder/baz/",
        "test_folder/baz/a",
        "test_folder/baz/b",
    ]

    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_copy_local_to_s3(self, MockS3Gateway):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        service.s3_gateway.upload_file = MagicMock(return_value=None)
        service.copy(self.LOCAL_FILE, self.S3_FILE)
        service.s3_gateway.upload_file.assert_called_with(
            str(self.LOCAL_FILE), "bucket", "test_file"
        )

    def test_copy_local_dir_to_s3_recursive_false(self):
        service = S3StorageService("us-west-1")
        with patch("os.path.isdir", return_value=True):
            self.assertRaises(
                ValueError, service.copy, self.LOCAL_FOLDER, self.S3_FOLDER, False
            )

    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_copy_local_dir_to_s3_recursive_true(self, MockS3Gateway):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        service.s3_gateway.put_object = MagicMock(return_value=None)
        service.s3_gateway.upload_file = MagicMock(return_value=None)

        with patch("os.path.isdir", return_value=True):
            with patch("os.walk", return_value=self.LOCAL_DIR):
                service.copy(self.LOCAL_FOLDER, self.S3_FOLDER, True)

                service.s3_gateway.put_object.assert_called_with(
                    "bucket", "test_folder/bar/", ""
                )

                service.s3_gateway.upload_file.assert_has_calls(
                    [
                        call("/foo/baz/a", "bucket", "test_folder/baz/a"),
                        call("/foo/baz/b", "bucket", "test_folder/baz/b"),
                    ],
                    any_order=True,
                )

    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_copy_s3_to_local(self, MockS3Gateway):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        service.s3_gateway.download_file = MagicMock(return_value=None)
        service.copy(self.S3_FILE, self.LOCAL_FILE)
        service.s3_gateway.download_file.assert_called_with(
            "bucket", "test_file", str(self.LOCAL_FILE)
        )

    def test_copy_s3_dir_to_local_recursive_false(self):
        service = S3StorageService("us-west-1")
        self.assertRaises(
            ValueError, service.copy, self.S3_FOLDER, self.LOCAL_FOLDER, False
        )

    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_copy_s3_dir_to_local_source_does_not_exist(self, MockS3Gateway):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        service.s3_gateway.object_exists = MagicMock(return_value=False)
        self.assertRaises(
            ValueError, service.copy, self.S3_FOLDER, self.LOCAL_FOLDER, False
        )

    @patch("os.makedirs")
    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_copy_s3_dir_to_local_ok(self, MockS3Gateway, os_makedirs):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        service.s3_gateway.object_exists = MagicMock(return_value=True)
        service.s3_gateway.list_object2 = MagicMock(return_value=self.S3_DIR)
        service.s3_gateway.download_file = MagicMock(return_value=None)

        service.copy(self.S3_FOLDER, self.LOCAL_FOLDER, True)

        os.makedirs.assert_has_calls(
            [
                call("/foo/bar"),
                call("/foo/baz"),
            ],
            any_order=True,
        )

        service.s3_gateway.download_file.assert_has_calls(
            [
                call("bucket", "test_folder/baz/a", "/foo/baz/a"),
                call("bucket", "test_folder/baz/b", "/foo/baz/b"),
            ],
            any_order=True,
        )

    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_copy_local_to_local(self, MockS3Gateway):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        self.assertRaises(ValueError, service.copy, self.LOCAL_FILE, self.LOCAL_FILE)

    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_copy_s3_to_s3(self, MockS3Gateway):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        service.copy(self.S3_FILE, self.S3_FILE_COPY)
        service.s3_gateway.copy.assert_called_with(
            "bucket", "test_file", "bucket", "test_file_copy"
        )

    def test_copy_s3_dir_to_s3_recursive_false(self):
        service = S3StorageService("us-west-1")
        self.assertRaises(
            ValueError, service.copy, self.S3_FOLDER, self.S3_FOLDER_COPY, False
        )

    def test_copy_s3_dir_to_s3_source_and_dest_are_the_same(self):
        service = S3StorageService("us-west-1")
        self.assertRaises(
            ValueError, service.copy, self.S3_FOLDER, self.S3_FOLDER, True
        )

    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_copy_s3_dir_to_s3_source_does_not_exist(self, MockS3Gateway):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        service.s3_gateway.object_exists = MagicMock(return_value=False)
        self.assertRaises(
            ValueError, service.copy, self.S3_FOLDER, self.S3_FOLDER_COPY, False
        )

    @patch("os.makedirs")
    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_copy_s3_dir_to_s3_ok(self, MockS3Gateway, os_makedirs):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        service.s3_gateway.object_exists = MagicMock(return_value=True)
        service.s3_gateway.list_object2 = MagicMock(return_value=self.S3_DIR)
        service.s3_gateway.put_object = MagicMock(return_value=None)
        service.s3_gateway.copy = MagicMock(return_value=None)

        service.copy(self.S3_FOLDER, self.S3_FOLDER_COPY, True)

        service.s3_gateway.put_object.assert_has_calls(
            [
                call("bucket", "test_folder_copy/bar/", ""),
                call("bucket", "test_folder_copy/baz/", ""),
            ],
            any_order=True,
        )

        service.s3_gateway.copy.assert_has_calls(
            [
                call("bucket", "test_folder/baz/a", "bucket", "test_folder_copy/baz/a"),
                call("bucket", "test_folder/baz/b", "bucket", "test_folder_copy/baz/b"),
            ],
            any_order=True,
        )

    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_delete_s3(self, MockS3Gateway):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        service.delete(self.S3_FILE)
        service.s3_gateway.delete_object.assert_called_with("bucket", "test_file")

    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_file_exists(self, MockS3Gateway):
        service = S3StorageService("us-west-1")

        service.s3_gateway = MockS3Gateway()
        service.file_exists(self.S3_FILE)
        service.s3_gateway.object_exists.assert_called_with("bucket", "test_file")

    @patch("fbpcp.gateway.s3.S3Gateway")
    def test_list_files(self, MockS3Gateway):
        service = S3StorageService("us-west-1")
        service.s3_gateway = MockS3Gateway()
        service.list_files(self.S3_FOLDER)
        service.s3_gateway.list_object2.assert_called_with("bucket", "test_folder")
