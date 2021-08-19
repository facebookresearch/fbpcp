#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fbpcp.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcp.entity.mpc_instance import MPCInstance, MPCInstanceStatus, MPCParty
from fbpcp.service.mpc import MPCService


TEST_INSTANCE_ID = "123"
TEST_GAME_NAME = "lift"
TEST_MPC_ROLE = MPCParty.SERVER
TEST_NUM_WORKERS = 1
TEST_SERVER_IPS = ["192.0.2.0", "192.0.2.1"]
TEST_INPUT_ARGS = "test_input_file"
TEST_OUTPUT_ARGS = "test_output_file"
TEST_CONCURRENCY_ARGS = 1
TEST_INPUT_DIRECTORY = "TEST_INPUT_DIRECTORY/"
TEST_OUTPUT_DIRECTORY = "TEST_OUTPUT_DIRECTORY/"
TEST_TASK_DEFINITION = "test_task_definition"
INPUT_DIRECTORY = "input_directory"
OUTPUT_DIRECTORY = "output_directory"
GAME_ARGS = [
    {
        "input_filenames": TEST_INPUT_ARGS,
        "input_directory": TEST_INPUT_DIRECTORY,
        "output_filenames": TEST_OUTPUT_ARGS,
        "output_directory": TEST_OUTPUT_DIRECTORY,
        "concurrency": TEST_CONCURRENCY_ARGS,
    }
]


class TestMPCService(unittest.TestCase):
    def setUp(self):
        cspatcher = patch("fbpcp.service.container.ContainerService")
        sspatcher = patch("fbpcp.service.storage.StorageService")
        irpatcher = patch("fbpcp.repository.mpc_instance_local.MPCInstanceRepository")
        gspatcher = patch("fbpcp.service.mpc_game.MPCGameService")
        container_svc = cspatcher.start()
        storage_svc = sspatcher.start()
        instance_repository = irpatcher.start()
        mpc_game_svc = gspatcher.start()
        for patcher in (cspatcher, sspatcher, irpatcher, gspatcher):
            self.addCleanup(patcher.stop)
        self.mpc_service = MPCService(
            container_svc,
            storage_svc,
            instance_repository,
            "test_task_definition",
            mpc_game_svc,
        )

    @staticmethod
    def _get_sample_mpcinstance():
        return MPCInstance.create_instance(
            instance_id=TEST_INSTANCE_ID,
            game_name=TEST_GAME_NAME,
            mpc_party=TEST_MPC_ROLE,
            num_workers=TEST_NUM_WORKERS,
            server_ips=TEST_SERVER_IPS,
            status=MPCInstanceStatus.CREATED,
            game_args=GAME_ARGS,
        )

    @staticmethod
    def _get_sample_mpcinstance_with_game_args():
        return MPCInstance.create_instance(
            instance_id=TEST_INSTANCE_ID,
            game_name=TEST_GAME_NAME,
            mpc_party=TEST_MPC_ROLE,
            num_workers=TEST_NUM_WORKERS,
            status=MPCInstanceStatus.CREATED,
            server_ips=TEST_SERVER_IPS,
            game_args=GAME_ARGS,
        )

    @staticmethod
    def _get_sample_mpcinstance_client():
        return MPCInstance.create_instance(
            instance_id=TEST_INSTANCE_ID,
            game_name=TEST_GAME_NAME,
            mpc_party=MPCParty.CLIENT,
            num_workers=TEST_NUM_WORKERS,
            server_ips=TEST_SERVER_IPS,
            status=MPCInstanceStatus.CREATED,
            game_args=GAME_ARGS,
        )

    async def test_spin_up_containers_onedocker_inconsistent_arguments(self):
        with self.assertRaisesRegex(
            ValueError,
            "The number of containers is not consistent with the number of game argument dictionary.",
        ):
            await self.mpc_service._spin_up_containers_onedocker(
                game_name=TEST_GAME_NAME,
                mpc_party=MPCParty.SERVER,
                num_containers=TEST_NUM_WORKERS,
                game_args=[],
            )

        with self.assertRaisesRegex(
            ValueError,
            "The number of containers is not consistent with number of ip addresses.",
        ):
            await self.mpc_service._spin_up_containers_onedocker(
                game_name=TEST_GAME_NAME,
                mpc_party=MPCParty.CLIENT,
                num_containers=TEST_NUM_WORKERS,
                ip_addresses=TEST_SERVER_IPS,
            )

    def test_create_instance_with_game_args(self):
        self.mpc_service.create_instance(
            instance_id=TEST_INSTANCE_ID,
            game_name=TEST_GAME_NAME,
            mpc_party=TEST_MPC_ROLE,
            num_workers=TEST_NUM_WORKERS,
            server_ips=TEST_SERVER_IPS,
            game_args=GAME_ARGS,
        )
        self.mpc_service.instance_repository.create.assert_called()
        self.assertEqual(
            self._get_sample_mpcinstance_with_game_args(),
            self.mpc_service.instance_repository.create.call_args[0][0],
        )

    def test_create_instance(self):
        self.mpc_service.create_instance(
            instance_id=TEST_INSTANCE_ID,
            game_name=TEST_GAME_NAME,
            mpc_party=TEST_MPC_ROLE,
            num_workers=TEST_NUM_WORKERS,
            server_ips=TEST_SERVER_IPS,
            game_args=GAME_ARGS,
        )
        # check that instance with correct instance_id was created
        self.mpc_service.instance_repository.create.assert_called()
        self.assertEquals(
            self._get_sample_mpcinstance(),
            self.mpc_service.instance_repository.create.call_args[0][0],
        )

    def _read_side_effect_start(self, instance_id: str):
        """mock MPCInstanceRepository.read for test_start"""
        if instance_id == TEST_INSTANCE_ID:
            return self._get_sample_mpcinstance()
        else:
            raise RuntimeError(f"{instance_id} does not exist")

    def test_start_instance(self):
        self.mpc_service.instance_repository.read = MagicMock(
            side_effect=self._read_side_effect_start
        )
        created_instances = [
            ContainerInstance(
                "arn:aws:ecs:us-west-1:592513842793:task/57850450-7a81-43cc-8c73-2071c52e4a68",  # noqa
                "10.0.1.130",
                ContainerInstanceStatus.STARTED,
            )
        ]
        self.mpc_service.container_svc.create_instances_async = AsyncMock(
            return_value=created_instances
        )
        built_onedocker_args = ("private_lift/lift", "test one docker arguments")
        self.mpc_service.mpc_game_svc.build_onedocker_args = MagicMock(
            return_value=built_onedocker_args
        )
        # check that update is called with correct status
        self.mpc_service.start_instance(TEST_INSTANCE_ID)
        self.mpc_service.instance_repository.update.assert_called()
        latest_update = self.mpc_service.instance_repository.update.call_args_list[-1]
        updated_status = latest_update[0][0].status
        self.assertEqual(updated_status, MPCInstanceStatus.STARTED)

    def test_start_instance_missing_ips(self):
        self.mpc_service.instance_repository.read = MagicMock(
            return_value=self._get_sample_mpcinstance_client()
        )
        # Exception because role is client but server ips are not given
        with self.assertRaises(ValueError):
            self.mpc_service.start_instance(TEST_INSTANCE_ID)

    def _read_side_effect_update(self, instance_id):
        """
        mock MPCInstanceRepository.read for test_update,
        with instance.containers is not None
        """
        if instance_id == TEST_INSTANCE_ID:
            mpc_instance = self._get_sample_mpcinstance()
        else:
            raise RuntimeError(f"{instance_id} does not exist")

        mpc_instance.status = MPCInstanceStatus.STARTED
        mpc_instance.containers = [
            ContainerInstance(
                "arn:aws:ecs:us-west-1:592513842793:task/57850450-7a81-43cc-8c73-2071c52e4a68",  # noqa
                "10.0.1.130",
                ContainerInstanceStatus.STARTED,
            )
        ]
        return mpc_instance

    def test_update_instance(self):
        self.mpc_service.instance_repository.read = MagicMock(
            side_effect=self._read_side_effect_update
        )
        container_instances = [
            ContainerInstance(
                "arn:aws:ecs:us-west-1:592513842793:task/cd34aed2-321f-49d1-8641-c54baff8b77b",  # noqa
                "10.0.1.130",
                ContainerInstanceStatus.STARTED,
            )
        ]
        self.mpc_service.container_svc.get_instances = MagicMock(
            return_value=container_instances
        )
        self.mpc_service.update_instance(TEST_INSTANCE_ID)
        self.mpc_service.instance_repository.update.assert_called()

    def test_stop_instance(self):
        self.mpc_service.instance_repository.read = MagicMock(
            side_effect=self._read_side_effect_update
        )
        self.mpc_service.onedocker_svc.stop_containers = MagicMock(return_value=[None])
        mpc_instance = self.mpc_service.stop_instance(TEST_INSTANCE_ID)
        self.mpc_service.onedocker_svc.stop_containers.assert_called_with(
            [
                "arn:aws:ecs:us-west-1:592513842793:task/57850450-7a81-43cc-8c73-2071c52e4a68"
            ]
        )
        expected_mpc_instance = self._read_side_effect_update(TEST_INSTANCE_ID)
        expected_mpc_instance.status = MPCInstanceStatus.CANCELED
        self.assertEqual(expected_mpc_instance, mpc_instance)
        self.mpc_service.instance_repository.update.assert_called_with(
            expected_mpc_instance
        )
