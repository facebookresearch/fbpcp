#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#############################################################################
# This test file is a short-term to freeze the file change during migration.
# After migration completed, we shall delete this ut test
# TODO: T137598681 clean up FBPCS mpc related files after migration complete
# NOTE: please make further change on fbcode/fbpcs/private_computation/service/mpc/
#############################################################################
import hashlib
import inspect
import unittest

from fbpcp.entity.mpc_game_config import MPCGameConfig
from fbpcp.entity.mpc_instance import MPCInstance
from fbpcp.repository.mpc_game_repository import MPCGameRepository
from fbpcp.repository.mpc_instance import MPCInstanceRepository

from fbpcp.service.mpc import MPCService
from fbpcp.service.mpc_game import MPCGameService

from .test_mpc import TestMPCService
from .test_mpc_game import TestMPCGameService

NO_CHANGE_FILES = (
    {
        "cls": MPCService,
        "file_md5": "45dc9ee0e1f36882c06c6959b3a7d365",
    },
    {
        "cls": TestMPCService,
        "file_md5": "6a1c7a74f28d164e113b68dbcab29962",
    },
    {
        "cls": MPCGameService,
        "file_md5": "b6e129eed50447bcbc7a7c0537771130",
    },
    {
        "cls": TestMPCGameService,
        "file_md5": "e1e4517471ff5630a7a7dc5db645ed5f",
    },
    {
        "cls": MPCGameConfig,
        "file_md5": "02d7ca709340b4fb6aa3f1a3d1616e29",
    },
    {
        "cls": MPCGameRepository,
        "file_md5": "3ce0126b0a3602c362789e6a17e1bb0e",
    },
    {
        "cls": MPCInstance,
        "file_md5": "f461fe24c29f68b1350c96567ddf28ef",
    },
    {
        "cls": MPCInstanceRepository,
        "file_md5": "9e3e1b712782fbec3f9a869d13954e08",
    },
)


class TestMPCDontChange(unittest.TestCase):
    def test_mpc_service_no_change(self):
        for no_change_file in NO_CHANGE_FILES:
            cls_name = no_change_file["cls"]
            file_name = inspect.getfile(cls_name)
            self.assertEqual(
                no_change_file["file_md5"],
                self.gen_file_md5(file_name),
                msg=f"assertion on file: {file_name}. you should change mpc in fbcode/fbpcs/private_computation/service/mpc/",
            )

    def gen_file_md5(self, file_name):
        with open(file_name, "rb") as file_to_check:
            data = file_to_check.read()
            # pipe contents of the file through
            return hashlib.md5(data).hexdigest()
