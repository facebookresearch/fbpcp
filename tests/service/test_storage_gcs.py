#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.service.storage_gcs import GCSStorageService


class TestGCSStorageService(unittest.TestCase):
    TEST_BUCKET = "test-bucket"
    TEST_FILE = "test-file"
    TEST_DATA = "this is test data"
    TEST_LOCAL_DIR = "./"
    TEST_LOCAL_FILE = "/test-local-file.txt"
    TEST_REMOTE_FILE = (
        "https://storage.cloud.google.com/" + TEST_BUCKET + "/" + TEST_FILE
    )

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    def test_read(self, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.gcs_gateway.get_object = MagicMock(return_value=None)
        gcs.read(self.TEST_REMOTE_FILE)
        gcs.gcs_gateway.get_object.assert_called()

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    def test_write(self, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.gcs_gateway.put_object = MagicMock(return_value=None)
        gcs.write(self.TEST_REMOTE_FILE, self.TEST_DATA)
        gcs.gcs_gateway.put_object.assert_called()

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    def test_copy_local_to_gcs(self, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        # test recursive upload
        gcs.upload_dir = MagicMock(return_value=None)
        gcs.copy(self.TEST_LOCAL_FILE, self.TEST_REMOTE_FILE, True)
        gcs.upload_dir.assert_called()
        # test non-recursive upload
        gcs.gcs_gateway.upload_file = MagicMock(return_value=None)
        gcs.copy(self.TEST_LOCAL_FILE, self.TEST_REMOTE_FILE, False)
        gcs.gcs_gateway.upload_file.assert_called_with(
            file_name=str(self.TEST_LOCAL_FILE),
            bucket=self.TEST_BUCKET,
            key=self.TEST_FILE,
        )

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    def test_copy_gcs_to_local(self, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.gcs_gateway.download_file = MagicMock(return_value=None)
        gcs.copy(self.TEST_REMOTE_FILE, self.TEST_LOCAL_FILE)
        gcs.gcs_gateway.download_file.assert_called_with(
            bucket=self.TEST_BUCKET,
            key=self.TEST_FILE,
            filename=str(self.TEST_LOCAL_FILE),
        )

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    @patch("glob.glob", return_value=["test.txt"])
    @patch("os.path.isfile", return_value=True)
    def test_upload_dir(self, isfile, glob, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.__check_dir = MagicMock(return_value=None)
        gcs.gcs_gateway.upload_file = MagicMock(return_value=None)
        gcs.upload_dir(self.TEST_LOCAL_DIR, self.TEST_BUCKET, self.TEST_FILE)
        gcs.gcs_gateway.upload_file.assert_called()

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    @patch("os.path.exists", return_value=True)
    def test_download_dir(self, exists, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.gcs_gateway = GCSGateway()
        gcs.gcs_gateway.list_objects = MagicMock(return_value=["test.txt"])
        gcs.gcs_gateway.download_file = MagicMock(return_value=None)
        gcs.download_dir(self.TEST_BUCKET, self.TEST_FILE, self.TEST_LOCAL_DIR)
        gcs.gcs_gateway.download_file.assert_called()

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    def test_copy_dir(self, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.gcs_gateway = GCSGateway()
        gcs.gcs_gateway.list_objects = MagicMock(return_value=["test.txt"])
        gcs.gcs_gateway.copy = MagicMock(return_value=None)
        gcs.copy_dir(
            self.TEST_BUCKET, self.TEST_FILE, self.TEST_BUCKET, self.TEST_FILE + "2"
        )
        gcs.gcs_gateway.copy.assert_called()

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    def test_delete(self, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.gcs_gateway = GCSGateway()
        gcs.gcs_gateway.delete_object = MagicMock(return_value=None)
        gcs.delete(self.TEST_REMOTE_FILE)
        gcs.gcs_gateway.delete_object.assert_called()

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    def test_file_exists(self, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.gcs_gateway = GCSGateway()
        gcs.gcs_gateway.object_exists = MagicMock(return_value=None)
        gcs.file_exists(self.TEST_REMOTE_FILE)
        gcs.gcs_gateway.object_exists.assert_called()

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    def test_get_file_info(self, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.gcs_gateway = GCSGateway()
        gcs.gcs_gateway.get_object_info = MagicMock(return_value={})
        gcs.get_file_info(self.TEST_REMOTE_FILE)
        gcs.gcs_gateway.get_object_info.assert_called()

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    def test_get_file_size(self, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.gcs_gateway = GCSGateway()
        gcs.gcs_gateway.get_object_size = MagicMock(return_value=None)
        gcs.get_file_size(self.TEST_REMOTE_FILE)
        gcs.gcs_gateway.get_object_size.assert_called()

    @patch("fbpcp.gateway.gcs.GCSGateway")
    @patch("google.cloud.storage.Client")
    def test_list_folders(self, GCSClient, GCSGateway):
        gcs = GCSStorageService()
        gcs.gcs_gateway = GCSGateway()
        gcs.gcs_gateway.list_objects = MagicMock(return_value=["test.txt"])
        gcs.list_folders(self.TEST_REMOTE_FILE)
        gcs.gcs_gateway.list_objects.assert_called()
