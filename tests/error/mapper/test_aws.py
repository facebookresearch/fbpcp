#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from botocore.exceptions import ClientError
from fbpcp.error.mapper.aws import map_aws_error
from fbpcp.error.pcp import PcpError, ThrottlingError


class TestMapAwsError(unittest.TestCase):
    def test_pcs_error(self):
        request_id = "76f3e69f-0d46-436f-803a-5e88956b7308"
        err = ClientError(
            {
                "Error": {
                    "Code": "Exception",
                    "Message": "test",
                },
                "ResponseMetadata": {
                    "RequestId": request_id,
                    "HTTPStatusCode": 400,
                },
            },
            "test",
        )
        err = map_aws_error(err)

        self.assertIsInstance(err, PcpError)
        self.assertIn(request_id, str(err))

    def test_throttling_error(self):
        request_id = "3e65a825-6a43-4261-b8a4-953972aa7065"
        err = ClientError(
            {
                "Error": {
                    "Code": "ThrottlingException",
                    "Message": "test",
                },
                "ResponseMetadata": {
                    "RequestId": request_id,
                    "HTTPStatusCode": 400,
                },
            },
            "test",
        )
        err = map_aws_error(err)

        self.assertIsInstance(err, ThrottlingError)
        self.assertIn(request_id, str(err))
