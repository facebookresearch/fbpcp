#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.gateway.s3 import S3Gateway


class TestS3Gateway(unittest.TestCase):
    TEST_LOCAL_FILE = "test-local-file"
    TEST_BUCKET = "test-bucket"
    TEST_FILE = "test-file"
    TEST_ACCESS_KEY_ID = "test-access-key-id"
    TEST_ACCESS_KEY_DATA = "test-access-key-data"
    REGION = "us-west-1"

    @patch("boto3.client")
    def test_create_bucket(self, BotoClient):
        gw = S3Gateway(self.REGION)
        gw.client = BotoClient()
        gw.client.create_bucket = MagicMock(return_value=None)
        gw.create_bucket(self.TEST_BUCKET)
        gw.client.create_bucket.assert_called()

    @patch("boto3.client")
    def test_delete_bucket(self, BotoClient):
        gw = S3Gateway(self.REGION)
        gw.client = BotoClient()
        gw.client.delete_bucket = MagicMock(return_value=None)
        gw.delete_bucket(self.TEST_BUCKET)
        gw.client.delete_bucket.assert_called()

    @patch("boto3.client")
    def test_put_object(self, BotoClient):
        gw = S3Gateway(self.REGION)
        gw.client = BotoClient()
        gw.client.put_object = MagicMock(return_value=None)
        gw.put_object(
            self.TEST_BUCKET, self.TEST_ACCESS_KEY_ID, self.TEST_ACCESS_KEY_DATA
        )
        gw.client.put_object.assert_called()

    @patch("os.path.getsize", return_value=100)
    @patch("boto3.client")
    def test_upload_file(self, BotoClient, mock_getsize):
        gw = S3Gateway(self.REGION)
        gw.client = BotoClient()
        gw.client.upload_file = MagicMock(return_value=None)
        gw.upload_file(self.TEST_LOCAL_FILE, self.TEST_BUCKET, self.TEST_FILE)
        gw.client.upload_file.assert_called()

    @patch("boto3.client")
    def test_download_file(self, BotoClient):
        gw = S3Gateway(self.REGION)
        gw.client = BotoClient()
        gw.client.head_object.return_value = {"ContentLength": 100}
        gw.client.download_file = MagicMock(return_value=None)
        gw.download_file(self.TEST_BUCKET, self.TEST_FILE, self.TEST_LOCAL_FILE)
        gw.client.download_file.assert_called()

    @patch("boto3.client")
    def test_delete_object(self, BotoClient):
        gw = S3Gateway(self.REGION)
        gw.client = BotoClient()
        gw.client.delete_object = MagicMock(return_value=None)
        gw.delete_object(self.TEST_BUCKET, self.TEST_FILE)
        gw.client.delete_object.assert_called()

    @patch("boto3.client")
    def test_copy(self, BotoClient):
        gw = S3Gateway(self.REGION)
        gw.client = BotoClient()
        gw.client.copy = MagicMock(return_value=None)
        gw.copy(
            self.TEST_BUCKET, self.TEST_FILE, self.TEST_BUCKET, f"{self.TEST_FILE}_COPY"
        )
        gw.client.copy.assert_called()

    @patch("boto3.client")
    def test_object_exists(self, BotoClient):
        gw = S3Gateway(self.REGION)
        gw.client = BotoClient()
        gw.client.head_object = MagicMock(return_value=None)
        self.assertTrue(gw.object_exists(self.TEST_BUCKET, self.TEST_ACCESS_KEY_ID))
        gw.client.head_object.assert_called()

    @patch("boto3.client")
    def test_object_not_exists(self, BotoClient):
        gw = S3Gateway(self.REGION)
        gw.client = BotoClient()
        gw.client.head_object = MagicMock(side_effect=Exception)
        self.assertFalse(gw.object_exists(self.TEST_BUCKET, self.TEST_ACCESS_KEY_ID))
        gw.client.head_object.assert_called()

    @patch("boto3.client")
    def test_list_object2(self, BotoClient):
        test_page_content_key1 = "test-page-content-key1"
        test_page_content_key2 = "test-page-content-key2"
        client_return_response = [
            {
                "Contents": [
                    {"Key": test_page_content_key1},
                    {"Key": test_page_content_key2},
                ],
            }
        ]
        gw = S3Gateway(self.REGION)
        gw.client = BotoClient()
        gw.client.get_paginator("list_objects_v2").paginate = MagicMock(
            return_value=client_return_response
        )
        key_list = gw.list_object2(self.TEST_BUCKET, self.TEST_ACCESS_KEY_ID)
        expected_key_list = [
            test_page_content_key1,
            test_page_content_key2,
        ]
        self.assertEqual(key_list, expected_key_list)
        gw.client.get_paginator("list_object_v2").paginate.assert_called()
