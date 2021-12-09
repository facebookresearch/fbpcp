#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import unittest

from fbpcp.error.mapper.gcp import map_gcp_error
from fbpcp.error.pcp import PcpError
from fbpcp.error.pcp import ThrottlingError
from google.cloud.exceptions import GoogleCloudError


class TestMapGCPError(unittest.TestCase):
    def test_pcs_error(self) -> None:
        err = GoogleCloudError("Test")
        err = map_gcp_error(err)

        self.assertIsInstance(err, PcpError)

    def test_throttling_error(self) -> None:
        err = GoogleCloudError("Test")
        err.code = 429
        err = map_gcp_error(err)

        self.assertIsInstance(err, ThrottlingError)
