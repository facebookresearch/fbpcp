#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from onedocker.common.core_dump_handler_aws import AWSCoreDumpHandler


class TestAWSCoreDumpHandler(unittest.TestCase):
    @patch("fbpcp.service.storage_s3.S3StorageService")
    def setUp(self, MockStorageService):
        self.aws_core_dump_handler = AWSCoreDumpHandler(MockStorageService)

    @patch("os.getcwd", return_value="/root/onedocker")
    @patch(
        "os.listdir",
        return_value=["a.out", "b.exe", "src", "core.20.2"],
    )
    def test_locate_core_dump_file(self, mock_listdir, mock_getcwd):
        expected_path = "/root/onedocker/core.20.2"
        test_path = self.aws_core_dump_handler.locate_core_dump_file()
        self.assertEqual(test_path, expected_path)

    @patch("uuid.uuid4", return_value="5f6ed2dd-7d99-4445-9419-8cc13c4adc6b")
    def test_upload_core_dump_file(self, mock_uuid):
        upload_dest = "http://test.s3.us-west-2.amazonaws.com/"
        core_file_path = "/root/onedocker/core.20.2"
        expected_s3_dest = f"{upload_dest}core.{mock_uuid.return_value}"
        self.aws_core_dump_handler.upload_core_dump_file(core_file_path, upload_dest)
        self.aws_core_dump_handler.storage_svc.copy.assert_called_with(
            core_file_path, expected_s3_dest
        )
