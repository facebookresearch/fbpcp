#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from onedocker.entity.opawdl_state import OPAWDLState
from onedocker.entity.opawdl_state_instance import (
    OPAWDLStateInstance,
    Status as StateStatus,
)
from onedocker.entity.opawdl_workflow import OPAWDLWorkflow
from onedocker.entity.opawdl_workflow_instance import (
    OPAWDLWorkflowInstance,
    Status as WorkflowStatus,
)
from onedocker.repository.opawdl_workflow_instance_repository_local import (
    LocalOPAWDLWorkflowInstanceRepository,
)


class TestLocalOPAWDLWorkflowInstanceRepository(unittest.TestCase):
    def setUp(self):
        self.test_plugin_name = "test_plugin"
        self.test_cmd_args_list = ["-a=b", "-c=d"]
        self.test_opawdl_state = OPAWDLState(
            plugin_name=self.test_plugin_name, cmd_args_list=self.test_cmd_args_list
        )
        self.test_opawdl_state_instance = OPAWDLStateInstance(
            opawdl_state=self.test_opawdl_state,
            status=StateStatus.COMPLETED,
        )
        self.test_state_name = "state_1"
        self.test_opawdl_workflow = OPAWDLWorkflow(
            starts_at=self.test_state_name,
            states={self.test_state_name: self.test_opawdl_state},
        )
        self.test_instance_id = "abcd"
        self.test_opawdl_workflow_instance = OPAWDLWorkflowInstance(
            instance_id=self.test_instance_id,
            opawdl_workflow=self.test_opawdl_workflow,
            state_instances=[self.test_opawdl_state_instance],
            status=WorkflowStatus.STARTED,
        )
        self.test_repo_directory = "test/dir/"
        self.workflow_repo = LocalOPAWDLWorkflowInstanceRepository(
            self.test_repo_directory
        )

    @patch("onedocker.repository.opawdl_workflow_instance_repository_local.Path.exists")
    def test_create(self, mock_path_exists):
        # Arrange
        test_file_path = Path(self.test_repo_directory).joinpath(
            self.test_opawdl_workflow_instance.get_instance_id()
        )
        mock_path_exists.return_value = False
        # Act
        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            self.workflow_repo.create(self.test_opawdl_workflow_instance)
        # Assert
        open_mock.assert_called_once_with(test_file_path, "w")
        open_mock.return_value.__enter__().write.assert_called_once_with(
            str(self.test_opawdl_workflow_instance)
        )

    @patch("onedocker.repository.opawdl_workflow_instance_repository_local.Path.exists")
    def test_create_raise_exception(self, mock_path_exists):
        # Arrange
        mock_path_exists.return_value = True
        # Act and Assert
        with self.assertRaisesRegex(
            Exception,
            f"Fail to create the workflow instance: {self.test_opawdl_workflow_instance.get_instance_id()} already exists.",
        ):
            self.workflow_repo.create(self.test_opawdl_workflow_instance)

    @patch("onedocker.repository.opawdl_workflow_instance_repository_local.Path.exists")
    def test_get(self, mock_path_exists):
        # Arrange
        test_file_path = Path(self.test_repo_directory).joinpath(self.test_instance_id)
        mock_path_exists.return_value = True
        # Act
        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            open_mock.return_value.__enter__().read.return_value = str(
                self.test_opawdl_workflow_instance
            )
            result = self.workflow_repo.get(self.test_instance_id)
        # Assert
        open_mock.assert_called_once_with(test_file_path, "r")
        self.assertEqual(result, self.test_opawdl_workflow_instance)

    @patch("onedocker.repository.opawdl_workflow_instance_repository_local.Path.exists")
    def test_get_raise_exception(self, mock_path_exists):
        # Arrange
        mock_path_exists.return_value = False
        # Act and Assert
        with patch("builtins.open"):
            with self.assertRaisesRegex(
                Exception,
                f"{self.test_instance_id} does NOT exist",
            ):
                self.workflow_repo.get(self.test_instance_id)

    @patch("onedocker.repository.opawdl_workflow_instance_repository_local.Path.exists")
    def test_update(self, mock_path_exists):
        # Arrange
        test_file_path = Path(self.test_repo_directory).joinpath(
            self.test_opawdl_workflow_instance.get_instance_id()
        )
        mock_path_exists.return_value = True
        # Act
        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            self.workflow_repo.update(self.test_opawdl_workflow_instance)
        # Assert
        open_mock.assert_called_once_with(test_file_path, "w")
        open_mock.return_value.__enter__().write.assert_called_once_with(
            str(self.test_opawdl_workflow_instance)
        )

    @patch("onedocker.repository.opawdl_workflow_instance_repository_local.Path.exists")
    def test_update_raise_exception(self, mock_path_exists):
        # Arrange
        mock_path_exists.return_value = False
        # Act and Assert
        with patch("builtins.open"):
            with self.assertRaisesRegex(
                Exception,
                f"{self.test_opawdl_workflow_instance.get_instance_id()} does not exist",
            ):
                self.workflow_repo.update(self.test_opawdl_workflow_instance)

    @patch("onedocker.repository.opawdl_workflow_instance_repository_local.Path.exists")
    @patch("onedocker.repository.opawdl_workflow_instance_repository_local.Path.unlink")
    def test_delete(self, mock_path_unlink, mock_path_exists):
        # Arrange
        test_file_path = Path(self.test_repo_directory).joinpath(
            self.test_opawdl_workflow_instance.get_instance_id()
        )
        # Act
        self.workflow_repo.delete(self.test_opawdl_workflow_instance.get_instance_id())
        # Assert
        test_file_path.unlink.assert_called_once()

    @patch("onedocker.repository.opawdl_workflow_instance_repository_local.Path.exists")
    def test_delete_raise_exception(self, mock_path_exists):
        # Arrange
        mock_path_exists.return_value = False
        # Act and Assert
        with self.assertRaisesRegex(
            Exception,
            f"{self.test_opawdl_workflow_instance.get_instance_id()} does not exist",
        ):
            self.workflow_repo.delete(
                self.test_opawdl_workflow_instance.get_instance_id()
            )
