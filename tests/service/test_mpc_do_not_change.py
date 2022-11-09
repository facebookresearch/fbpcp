#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import hashlib
import inspect
import unittest

from fbpcp.service.mpc import MPCService
from fbpcp.service.mpc_game import MPCGameService

from .test_mpc import TestMPCService
from .test_mpc_game import TestMPCGameService

NO_CHANGE_FILES = (
    {
        "cls": MPCService,
        "file_md5": "35dbe2a73b1016d6d631b03abc612929",
    },
    {
        "cls": TestMPCService,
        "file_md5": "6a1c7a74f28d164e113b68dbcab29962",
    },
    {
        "cls": MPCGameService,
        "file_md5": "36a2142e36759e382855e970f12c7403",
    },
    {
        "cls": TestMPCGameService,
        "file_md5": "e1e4517471ff5630a7a7dc5db645ed5f",
    },
)


class TestMPCDontChange(unittest.TestCase):
    def test_mpc_service_no_change(self):
        for no_change_file in NO_CHANGE_FILES:
            cls_name = no_change_file["cls"]
            file_name = inspect.getfile(cls_name)
            self.assertEqual(no_change_file["file_md5"], self.gen_file_md5(file_name))

    def gen_file_md5(self, file_name):
        with open(file_name, "rb") as file_to_check:
            data = file_to_check.read()
            # pipe contents of the file through
            return hashlib.md5(data).hexdigest()
