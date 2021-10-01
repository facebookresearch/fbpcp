#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.gateway.gcs import GCSGateway


class TestGCSGateway(unittest.TestCase):
    TEST_LOCAL_FILE = "test-local-file"
    TEST_BUCKET = "test-bucket"
    TEST_FILE = "test-file"
    TEST_OBJECT_NAME = "test-object-name"
    TEST_OBJECT_DATA = "test-object-data"
    REGION = "US"

    @patch("google.cloud.storage.Client")
    def test_create_bucket(self, GCSClient):
        gw = GCSGateway(self.REGION)
        gw.client = GCSClient()
        gw.client.create_bucket = MagicMock(return_value=None)
        gw.create_bucket(self.TEST_BUCKET)
        gw.client.create_bucket.assert_called()

    @patch("google.cloud.storage.Client")
    def test_delete_bucket(self, GCSClient):
        gw = GCSGateway(self.REGION)
        gw.client = GCSClient()
        gw.client.get_bucket(self.TEST_BUCKET).delete = MagicMock(return_value=None)
        gw.delete_bucket(self.TEST_BUCKET)
        gw.client.get_bucket(self.TEST_BUCKET).delete.assert_called()

    @patch("google.cloud.storage.Client")
    def test_put_object(self, GCSClient):
        gw = GCSGateway(self.REGION)
        gw.client = GCSClient()
        gw.client.bucket(self.TEST_BUCKET).blob(
            self.TEST_OBJECT_NAME
        ).upload_from_string = MagicMock(return_value=None)
        gw.put_object(self.TEST_BUCKET, self.TEST_OBJECT_NAME, self.TEST_OBJECT_DATA)
        gw.client.bucket(self.TEST_BUCKET).blob(
            self.TEST_OBJECT_NAME
        ).upload_from_string.assert_called()

    @patch("google.cloud.storage.Client")
    def test_upload_file(self, GCSClient):
        gw = GCSGateway(self.REGION)
        gw.client = GCSClient()
        gw.client.bucket(self.TEST_BUCKET).blob(
            self.TEST_OBJECT_NAME
        ).upload_from_filename = MagicMock(return_value=None)
        gw.upload_file(self.TEST_BUCKET, self.TEST_LOCAL_FILE, self.TEST_FILE)
        gw.client.bucket(self.TEST_BUCKET).blob(
            self.TEST_OBJECT_NAME
        ).upload_from_filename.assert_called()

    @patch("google.cloud.storage.Client")
    def test_download_file(self, GCSClient):
        gw = GCSGateway(self.REGION)
        gw.client = GCSClient()
        gw.client.bucket(self.TEST_BUCKET).blob(
            self.TEST_OBJECT_NAME
        ).download_to_filename = MagicMock(return_value=None)
        gw.download_file(self.TEST_BUCKET, self.TEST_FILE, self.TEST_LOCAL_FILE)
        gw.client.bucket(self.TEST_BUCKET).blob(
            self.TEST_OBJECT_NAME
        ).download_to_filename.assert_called()

    @patch("google.cloud.storage.Client")
    def test_delete_object(self, GCSClient):
        gw = GCSGateway(self.REGION)
        gw.client = GCSClient()
        gw.client.bucket(self.TEST_BUCKET).blob(self.TEST_FILE).delete = MagicMock(
            return_value=None
        )
        gw.delete_object(self.TEST_BUCKET, self.TEST_FILE)
        gw.client.bucket(self.TEST_BUCKET).blob(self.TEST_FILE).delete.assert_called()

    @patch("google.cloud.storage.Client")
    def test_copy(self, GCSClient):
        gw = GCSGateway(self.REGION)
        gw.client = GCSClient()
        gw.client.bucket(self.TEST_BUCKET).copy_blob = MagicMock(return_value=None)
        gw.copy(
            self.TEST_BUCKET, self.TEST_FILE, self.TEST_BUCKET, f"{self.TEST_FILE}_COPY"
        )
        gw.client.bucket(self.TEST_BUCKET).copy_blob.assert_called()

    @patch("google.cloud.storage.Client")
    def test_object_exists(self, GCSClient):
        gw = GCSGateway(self.REGION)
        gw.client = GCSClient()
        gw.client.bucket(self.TEST_BUCKET).blob(self.TEST_FILE).exists = MagicMock(
            return_value=None
        )
        gw.object_exists(self.TEST_BUCKET, self.TEST_FILE)
        gw.client.bucket(self.TEST_BUCKET).blob(self.TEST_FILE).exists.assert_called()

    @patch("google.cloud.storage.Client")
    def test_list_objects(self, GCSClient):
        gw = GCSGateway(self.REGION)
        gw.client = GCSClient()
        gw.client.list_blobs = MagicMock(return_value=[])
        gw.list_objects(self.TEST_BUCKET, self.TEST_FILE)
        gw.client.list_blobs.assert_called()
