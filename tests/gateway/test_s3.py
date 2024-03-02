#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

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
TEST_SESSION_TOKEN = "test-session-token"
TEST_S3_OPERATION = "head_object"
TEST_BASE_BUCKET_PATH = "lift"
TEST_DEFAULT_CONFIG = {}
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
    def test_get_policy_statements(self, BotoClient):
        # Arrage
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        response = {
            "Policy": '{"Version":"2008-10-17","Statement":[]}',
            "ResponseMetadata": {
                "...": "...",
            },
        }
        gw.client.get_bucket_policy = MagicMock(return_value=response)
        # Act
        policy_statements = gw.get_policy_statements(TEST_BUCKET)
        # Assert
        gw.client.get_bucket_policy.assert_called_with(Bucket=TEST_BUCKET)
        self.assertEqual(len(policy_statements), 0)

    @patch("boto3.client")
    def test_get_public_access_block(self, BotoClient):
        # Arrage
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        response = {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            }
        }
        gw.client.get_public_access_block = MagicMock(return_value=response)
        # Act
        gw.get_public_access_block(TEST_BUCKET)
        # Assert
        gw.client.get_public_access_block.assert_called_with(Bucket=TEST_BUCKET)

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

    @patch("boto3.client")
    def test_auth_keys(self, mock_boto_client):
        gateway = S3Gateway(REGION, TEST_ACCESS_KEY_ID, TEST_ACCESS_KEY_DATA)
        expected_config = {
            "aws_access_key_id": TEST_ACCESS_KEY_ID,
            "aws_secret_access_key": TEST_ACCESS_KEY_DATA,
        }

        mock_boto_client.assert_called_with(
            "s3",
            region_name=REGION,
            aws_access_key_id=TEST_ACCESS_KEY_ID,
            aws_secret_access_key=TEST_ACCESS_KEY_DATA,
        )
        self.assertEqual(gateway.config, expected_config)

    @patch("boto3.client")
    def test_session_auth_keys(self, mock_boto_client):
        gateway = S3Gateway(
            REGION,
            TEST_ACCESS_KEY_ID,
            TEST_ACCESS_KEY_DATA,
            TEST_DEFAULT_CONFIG,
            TEST_SESSION_TOKEN,
        )
        expected_config = {
            "aws_access_key_id": TEST_ACCESS_KEY_ID,
            "aws_secret_access_key": TEST_ACCESS_KEY_DATA,
            "aws_session_token": TEST_SESSION_TOKEN,
        }

        mock_boto_client.assert_called_with(
            "s3",
            region_name=REGION,
            aws_access_key_id=TEST_ACCESS_KEY_ID,
            aws_secret_access_key=TEST_ACCESS_KEY_DATA,
            aws_session_token=TEST_SESSION_TOKEN,
        )
        self.assertEqual(gateway.config, expected_config)

    @patch("boto3.client")
    def test_list_folders_returns_processed_list(self, BotoClient):
        test_prefix1 = f"{TEST_BASE_BUCKET_PATH}/binary/binary1/"
        test_prefix2 = f"{TEST_BASE_BUCKET_PATH}/binary2/binary/"
        client_return_response = {
            "CommonPrefixes": [
                {"Prefix": test_prefix1},
                {"Prefix": test_prefix2},
            ],
        }
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.list_objects_v2 = MagicMock(return_value=client_return_response)
        key_list = gw.list_folders(TEST_BUCKET, TEST_BASE_BUCKET_PATH)
        expected_key_list = [
            "binary/binary1",
            "binary2/binary",
        ]
        self.assertEqual(key_list, expected_key_list)
        gw.client.list_objects_v2.assert_called_once()

    @patch("boto3.client")
    def test_list_folders_returns_empty_list_if_response_is_empty(self, BotoClient):
        client_return_response = {}
        gw = S3Gateway(REGION)
        gw.client = BotoClient()
        gw.client.list_objects_v2 = MagicMock(return_value=client_return_response)
        key_list = gw.list_folders(TEST_BUCKET, TEST_BASE_BUCKET_PATH)

        self.assertEqual(key_list, [])
        gw.client.list_objects_v2.assert_called_once()
