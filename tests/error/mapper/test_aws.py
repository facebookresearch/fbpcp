#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from botocore.exceptions import ClientError
from fbpcs.error.mapper.aws import map_aws_error
from fbpcs.error.pcs import PcsError
from fbpcs.error.pcs import ThrottlingError


class TestMapAwsError(unittest.TestCase):
    def test_pcs_error(self):
        err = ClientError(
            {
                "Error": {
                    "Code": "Exception",
                    "Message": "test",
                },
            },
            "test",
        )
        err = map_aws_error(err)

        self.assertIsInstance(err, PcsError)

    def test_throttling_error(self):
        err = ClientError(
            {
                "Error": {
                    "Code": "ThrottlingException",
                    "Message": "test",
                },
            },
            "test",
        )
        err = map_aws_error(err)

        self.assertIsInstance(err, ThrottlingError)
