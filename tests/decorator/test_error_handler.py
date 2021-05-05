#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from botocore.exceptions import ClientError
from fbpcs.decorator.error_handler import error_handler
from fbpcs.error.pcs import PcsError
from fbpcs.error.throttling import ThrottlingError


class TestErrorHandler(unittest.TestCase):
    def test_pcs_error(self):
        @error_handler
        def foo():
            raise ValueError("just a test")

        self.assertRaises(PcsError, foo)

    def test_throttling_error(self):
        @error_handler
        def foo():
            err = ClientError(
                {
                    "Error": {
                        "Code": "ThrottlingException",
                        "Message": "test",
                    },
                },
                "test",
            )

            raise err

        self.assertRaises(ThrottlingError, foo)
