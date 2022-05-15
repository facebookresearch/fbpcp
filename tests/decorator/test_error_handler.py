#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from botocore.exceptions import ClientError
from fbpcp.decorator.error_handler import error_handler
from fbpcp.error.pcp import PcpError, ThrottlingError
from google.cloud.exceptions import TooManyRequests


class TestErrorHandler(unittest.TestCase):
    def test_pcs_error(self):
        @error_handler
        def foo():
            raise ValueError("just a test")

        self.assertRaises(PcpError, foo)

    def test_throttling_error(self):
        @error_handler
        def foo():
            err = ClientError(
                {
                    "Error": {
                        "Code": "ThrottlingException",
                        "Message": "test",
                    },
                    "ResponseMetadata": {
                        "RequestId": "test_id",
                        "HTTPStatusCode": 400,
                    },
                },
                "test",
            )

            raise err

        self.assertRaises(ThrottlingError, foo)

    def test_wrapped_function_args(self):
        @error_handler
        def foo(**kwargs):
            raise ValueError("just a test f")

        error_msgs = {
            "error_type1": "error_msg1",
            "error_type2": "error_msg2",
        }
        self.assertRaises(PcpError, foo, error_msgs)

    def test_wrapped_function_kwargs(self):
        @error_handler
        def foo(*args):
            raise ValueError("just a test")

        self.assertRaises(PcpError, foo, "error1", "error2")

    def test_gcp_throttling_error(self):
        @error_handler
        def foo():
            # Exception mapping a 429 Too Many Requests response
            err = TooManyRequests("test")
            raise err

        self.assertRaises(ThrottlingError, foo)
