#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import uuid
from unittest.mock import MagicMock, mock_open, patch

from onedocker.entity.opawdl_state import OPAWDLState
from onedocker.entity.opawdl_workflow import OPAWDLWorkflow
from onedocker.service.opawdl_driver import OPAWDLDriver


class TestOPAWDLDriver(unittest.TestCase):
    @patch(
        "onedocker.repository.opawdl_workflow_instance_repository_local.LocalOPAWDLWorkflowInstanceRepository"
    )
    def setUp(self, MockLocalOPAWDLWorkflowRepository):
        self.test_plugin_name = "test_plugin"
        self.test_cmd_args_list = ["-a=b", "-c=d"]
        self.test_opawdl_state = OPAWDLState(
            plugin_name=self.test_plugin_name, cmd_args_list=self.test_cmd_args_list
        )
        self.test_state_name = "state_1"
        self.test_opawdl_workflow = OPAWDLWorkflow(
            starts_at=self.test_state_name,
            states={self.test_state_name: self.test_opawdl_state},
        )
        self.test_opawdl_workflow_path = "test_workflow.json"
        self.test_workflow_instance_id = str(uuid.uuid4())
        self.mock_opawdl_repo = MockLocalOPAWDLWorkflowRepository("test_repo_path")

    @patch("onedocker.util.opawdl_parser.OPAWDLParser.parse_json_str_to_workflow")
    @patch("onedocker.service.opawdl_driver.subprocess.run")
    def test_run_workflow(
        self, mock_subprocess_run, mock_parse_json_str_to_workflow
    ) -> None:
        # Arrange
        self.mock_opawdl_repo.create.return_value = MagicMock()
        self.mock_opawdl_repo.update.return_value = MagicMock()
        mock_parse_json_str_to_workflow.return_value = self.test_opawdl_workflow
        expected_executed_cmd = (
            self.test_plugin_name + " " + " ".join(self.test_cmd_args_list)
        )

        # Act
        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            driver = OPAWDLDriver(
                instance_id=self.test_workflow_instance_id,
                workflow_path=self.test_opawdl_workflow_path,
                repo=self.mock_opawdl_repo,
            )
            driver.run_workflow()

        # Assert
        open_mock.assert_called_once_with(self.test_opawdl_workflow_path, "r")
        mock_subprocess_run.assert_called_once_with(expected_executed_cmd, shell=True)
