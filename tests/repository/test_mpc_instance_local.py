#!/usr/bin/env python3

import copy
import pickle
import unittest
from pathlib import Path
from unittest.mock import mock_open, MagicMock, patch

from fbpcs.entity.mpc_instance import MPCInstance, MPCInstanceStatus, MPCRole
from fbpcs.repository.mpc_instance_local import LocalMPCInstanceRepository

TEST_BASE_DIR = Path("./")
TEST_INSTANCE_ID = "test-instance-id"
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


class TestLocalMPCInstanceRepository(unittest.TestCase):
    def setUp(self):
        self.mpc_instance = MPCInstance(
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
        self.local_instance_repo = LocalMPCInstanceRepository(TEST_BASE_DIR)

    def test_create_existing_instance(self):
        self.local_instance_repo.repo._exist = MagicMock(return_value=True)
        with self.assertRaisesRegex(RuntimeError, ERROR_MSG_ALREADY_EXISTS):
            self.local_instance_repo.create(self.mpc_instance)

    @patch("builtins.open")
    @patch("pickle.dump")
    def test_create_non_existing_instance(self, mock_dump, mock_open):
        self.local_instance_repo.repo._exist = MagicMock(return_value=False)
        path = TEST_BASE_DIR.joinpath(TEST_INSTANCE_ID)
        mock_dump.return_value = None
        stream = mock_open().__enter__.return_value
        self.assertIsNone(self.local_instance_repo.create(self.mpc_instance))
        mock_open.assert_called_with(path, "wb")
        mock_dump.assert_called_with(self.mpc_instance, stream)

    def test_read_non_existing_instance(self):
        self.local_instance_repo.repo._exist = MagicMock(return_value=False)
        with self.assertRaisesRegex(RuntimeError, ERROR_MSG_NOT_EXISTS):
            self.local_instance_repo.read(TEST_INSTANCE_ID)

    def test_read_existing_instance(self):
        self.local_instance_repo.repo._exist = MagicMock(return_value=True)
        data = pickle.dumps(self.mpc_instance)
        path = TEST_BASE_DIR.joinpath(TEST_INSTANCE_ID)
        with patch("builtins.open", mock_open(read_data=data)) as mock_file:
            self.assertEqual(open(path).read(), data)
            mpc_instance = self.local_instance_repo.read(TEST_INSTANCE_ID)
            self.assertEqual(self.mpc_instance, mpc_instance)
            mock_file.assert_called_with(path, "rb")

    def test_update_non_existing_instance(self):
        self.local_instance_repo.repo._exist = MagicMock(return_value=False)
        with self.assertRaisesRegex(RuntimeError, ERROR_MSG_NOT_EXISTS):
            self.local_instance_repo.update(self.mpc_instance)

    @patch("builtins.open")
    @patch("pickle.dump")
    def test_update_existing_instance(self, mock_dump, mock_open):
        self.local_instance_repo.repo._exist = MagicMock(return_value=True)
        new_mpc_instance = copy.deepcopy(self.mpc_instance)
        new_mpc_instance.game_name = "aggregator"
        path = TEST_BASE_DIR.joinpath(TEST_INSTANCE_ID)
        mock_dump.return_value = None
        stream = mock_open().__enter__.return_value
        self.assertIsNone(self.local_instance_repo.update(new_mpc_instance))
        mock_open.assert_called_with(path, "wb")
        mock_dump.assert_called_with(new_mpc_instance, stream)

    def test_delete_non_existing_instance(self):
        self.local_instance_repo.repo._exist = MagicMock(return_value=False)
        with self.assertRaisesRegex(RuntimeError, ERROR_MSG_NOT_EXISTS):
            self.local_instance_repo.delete(TEST_INSTANCE_ID)

    def test_delete_existing_instance(self):
        with patch.object(Path, "joinpath") as mock_join:
            with patch.object(Path, "unlink") as mock_unlink:
                mock_unlink.return_value = None
                self.assertIsNone(self.local_instance_repo.delete(TEST_INSTANCE_ID))
                mock_join.assert_called_with(TEST_INSTANCE_ID)
