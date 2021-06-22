#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import pickle
import unittest
import uuid
from unittest.mock import MagicMock

from fbpcs.entity.mpc_instance import MPCInstance, MPCInstanceStatus, MPCRole
from fbpcs.repository.mpc_instance_s3 import S3MPCInstanceRepository
from fbpcs.service.storage_s3 import S3StorageService

TEST_BASE_DIR = "./"
TEST_INSTANCE_ID = str(uuid.uuid4())
TEST_GAME_NAME = "lift"
TEST_MPC_ROLE = MPCRole.SERVER
TEST_NUM_WORKERS = 1
TEST_SERVER_IPS = ["192.0.2.0"]
TEST_INPUT_ARGS = [{"input_filenames": "test_input_file"}]
TEST_OUTPUT_ARGS = [{"output_filenames": "test_output_file"}]
TEST_CONCURRENCY_ARGS = {"concurrency": 1}
TEST_INPUT_DIRECTORY = "TEST_INPUT_DIRECTORY/"
TEST_OUTPUT_DIRECTORY = "TEST_OUTPUT_DIRECTORY/"
ERROR_MSG_ALREADY_EXISTS = f"{TEST_INSTANCE_ID} already exists"
ERROR_MSG_NOT_EXISTS = f"{TEST_INSTANCE_ID} does not exist"


class TestS3InstanceRepository(unittest.TestCase):
    def setUp(self):
        storage_svc = S3StorageService("us-west-1")
        self.s3_storage_repo = S3MPCInstanceRepository(storage_svc, TEST_BASE_DIR)
        self.mpc_instance = MPCInstance.create_instance(
            instance_id=TEST_INSTANCE_ID,
            game_name=TEST_GAME_NAME,
            mpc_role=TEST_MPC_ROLE,
            num_workers=TEST_NUM_WORKERS,
            server_ips=TEST_SERVER_IPS,
            status=MPCInstanceStatus.CREATED,
            input_args=TEST_INPUT_ARGS,
            output_args=TEST_OUTPUT_ARGS,
            concurrency_args=TEST_CONCURRENCY_ARGS,
            input_directory=TEST_INPUT_DIRECTORY,
            output_directory=TEST_OUTPUT_DIRECTORY,
        )

    def test_create_non_existing_instance(self):
        self.s3_storage_repo.repo._exist = MagicMock(return_value=False)
        self.s3_storage_repo.repo.s3_storage_svc.write = MagicMock(return_value=None)
        self.s3_storage_repo.create(self.mpc_instance)
        self.s3_storage_repo.repo.s3_storage_svc.write.assert_called()

    def test_create_existing_instance(self):
        self.s3_storage_repo.repo._exist = MagicMock(
            side_effect=RuntimeError(ERROR_MSG_ALREADY_EXISTS)
        )
        with self.assertRaisesRegex(RuntimeError, ERROR_MSG_ALREADY_EXISTS):
            self.s3_storage_repo.create(self.mpc_instance)

    def test_read_non_existing_instance(self):
        self.s3_storage_repo.repo._exist = MagicMock(
            side_effect=RuntimeError(ERROR_MSG_NOT_EXISTS)
        )
        with self.assertRaisesRegex(RuntimeError, ERROR_MSG_NOT_EXISTS):
            self.s3_storage_repo.read(TEST_INSTANCE_ID)

    def test_read_existing_instance(self):
        self.s3_storage_repo.repo._exist = MagicMock(return_value=True)
        self.s3_storage_repo.repo.s3_storage_svc.read = MagicMock(
            return_value=pickle.dumps(self.mpc_instance, 0).decode()
        )
        instance = self.s3_storage_repo.read(self.mpc_instance)
        self.assertEqual(self.mpc_instance, instance)

    def test_update_non_existing_instance(self):
        self.s3_storage_repo.repo._exist = MagicMock(
            side_effect=RuntimeError(ERROR_MSG_NOT_EXISTS)
        )
        with self.assertRaisesRegex(RuntimeError, ERROR_MSG_NOT_EXISTS):
            self.s3_storage_repo.update(self.mpc_instance)

    def test_update_existing_instance(self):
        self.s3_storage_repo.repo._exist = MagicMock(return_value=True)
        self.s3_storage_repo.repo.s3_storage_svc.write = MagicMock(return_value=None)
        self.s3_storage_repo.update(self.mpc_instance)
        self.s3_storage_repo.repo.s3_storage_svc.write.assert_called()

    def test_delete_non_existing_instance(self):
        self.s3_storage_repo.repo._exist = MagicMock(
            side_effect=RuntimeError(ERROR_MSG_NOT_EXISTS)
        )
        with self.assertRaisesRegex(RuntimeError, ERROR_MSG_NOT_EXISTS):
            self.s3_storage_repo.delete(TEST_INSTANCE_ID)

    def test_delete_existing_instance(self):
        self.s3_storage_repo.repo._exist = MagicMock(return_value=True)
        self.s3_storage_repo.repo.s3_storage_svc.delete = MagicMock(return_value=None)
        self.s3_storage_repo.delete(TEST_INSTANCE_ID)
        self.s3_storage_repo.repo.s3_storage_svc.delete.assert_called()

    def test_exists(self):
        self.s3_storage_repo.repo.s3_storage_svc.file_exists = MagicMock(
            return_value=True
        )
        self.assertTrue(self.s3_storage_repo.repo._exist(TEST_INSTANCE_ID))
