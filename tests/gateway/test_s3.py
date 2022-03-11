#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError
from fbpcp.error.pcp import PcpError
from fbpcp.gateway.s3 import S3Gateway

TEST_LOCAL_FILE = "test-local-file"
TEST_BUCKET = "test-bucket"
TEST_FILE = "test-file"
TEST_ACCESS_KEY_ID = "test-access-key-id"
TEST_ACCESS_KEY_DATA = "test-access-key-data"
TEST_S3_OPERATION = "head_object"
REGION = "us-west-1"


class TestS3Gateway(unittest.TestCase):
    @patch("boto3.client")
    def test_create_bucket(self, BotoClient):
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.create_bucket = MagicMock(return_value=None)
        gw.create_bucket(TEST_BUCKET)
        gw.client.create_bucket.assert_called()

    @patch("boto3.client")
    def test_delete_bucket(self, BotoClient):
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.delete_bucket = MagicMock(return_value=None)
        gw.delete_bucket(TEST_BUCKET)
        gw.client.delete_bucket.assert_called()

    @patch("boto3.client")
    def test_put_object(self, BotoClient):
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.put_object = MagicMock(return_value=None)
        gw.put_object(TEST_BUCKET, TEST_ACCESS_KEY_ID, TEST_ACCESS_KEY_DATA)
        gw.client.put_object.assert_called()

    @patch("os.path.getsize", return_value=100)
    @patch("boto3.client")
    def test_upload_file(self, BotoClient, mock_getsize):
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.upload_file = MagicMock(return_value=None)
        gw.upload_file(TEST_LOCAL_FILE, TEST_BUCKET, TEST_FILE)
        gw.client.upload_file.assert_called()

    @patch("boto3.client")
    def test_download_file(self, BotoClient):
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.head_object.return_value = {"ContentLength": 100}
        gw.client.download_file = MagicMock(return_value=None)
        gw.download_file(TEST_BUCKET, TEST_FILE, TEST_LOCAL_FILE)
        gw.client.download_file.assert_called()

    @patch("boto3.client")
    def test_delete_object(self, BotoClient):
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.delete_object = MagicMock(return_value=None)
        gw.delete_object(TEST_BUCKET, TEST_FILE)
        gw.client.delete_object.assert_called()

    @patch("boto3.client")
    def test_copy(self, BotoClient):
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.copy = MagicMock(return_value=None)
        gw.copy(TEST_BUCKET, TEST_FILE, TEST_BUCKET, f"{TEST_FILE}_COPY")
        gw.client.copy.assert_called()

    @patch("boto3.client")
    def test_object_exists(self, BotoClient):
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.head_object = MagicMock(return_value=None)
        self.assertTrue(gw.object_exists(TEST_BUCKET, TEST_ACCESS_KEY_ID))
        gw.client.head_object.assert_called()

    @patch("boto3.client")
    def test_object_not_exists(self, BotoClient):
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
        gw.client.head_object = MagicMock(
            side_effect=ClientError(error_response, TEST_S3_OPERATION)
        )
        self.assertFalse(gw.object_exists(TEST_BUCKET, TEST_ACCESS_KEY_ID))
        gw.client.head_object.assert_called()

    @patch("boto3.client")
    def test_object_exists_exception(self, BotoClient):
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        error_code = "403"
        error_msg = "Permission denied"
        error_response = {
            "Error": {"Code": error_code, "Message": error_msg},
            "ResponseMetadata": {},
        }
        gw.client.head_object = MagicMock(
            side_effect=ClientError(error_response, TEST_S3_OPERATION)
        )
        with self.assertRaises(
            PcpError,
            msg=f"An error occurred ({error_code}) when calling the {TEST_S3_OPERATION} operation: {error_msg}",
        ):
            gw.object_exists(TEST_BUCKET, TEST_ACCESS_KEY_ID)

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
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.get_paginator("list_objects_v2").paginate = MagicMock(
            return_value=client_return_response
        )
        key_list = gw.list_object2(TEST_BUCKET, TEST_ACCESS_KEY_ID)
        expected_key_list = [
            test_page_content_key1,
            test_page_content_key2,
        ]
        self.assertEqual(key_list, expected_key_list)
        gw.client.get_paginator("list_object_v2").paginate.assert_called()
