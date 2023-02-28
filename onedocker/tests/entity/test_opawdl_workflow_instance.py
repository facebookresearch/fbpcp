#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import unittest

import onedocker.entity.opawdl_state_instance as state_instance
import onedocker.entity.opawdl_workflow_instance as workflow_instance

from onedocker.entity.opawdl_state import OPAWDLState
from onedocker.entity.opawdl_workflow import OPAWDLWorkflow


class TestOPAWDLWorkflowInstance(unittest.TestCase):
    def setUp(self) -> None:
        self.test_plugin_name = "test_plugin"
        self.test_cmd_args_list = ["-a=b", "-c=d"]
        self.test_opawdl_state = OPAWDLState(
            plugin_name=self.test_plugin_name, cmd_args_list=self.test_cmd_args_list
        )
        self.test_opawdl_state_instance = state_instance.OPAWDLStateInstance(
            opawdl_state=self.test_opawdl_state,
            status=state_instance.Status.COMPLETED,
        )
        self.test_state_name = "state_1"
        self.test_opawdl_workflow = OPAWDLWorkflow(
            starts_at=self.test_state_name,
            states={self.test_state_name: self.test_opawdl_state},
        )
        self.test_instance_id = "abcd"
        self.test_opawdl_workflow_instance = workflow_instance.OPAWDLWorkflowInstance(
            instance_id=self.test_instance_id,
            opawdl_workflow=self.test_opawdl_workflow,
            state_instances=[self.test_opawdl_state_instance],
            status=workflow_instance.Status.STARTED,
        )

    def test_get_instance_id(self) -> None:
        # Act and Assert
        self.assertEqual(
            self.test_opawdl_workflow_instance.get_instance_id(), self.test_instance_id
        )

    def test__str__(self) -> None:
        # Arrange
        expected_opawdl_workflow_instance_json_str = json.dumps(
            {
                "instance_id": self.test_instance_id,
                "opawdl_workflow": {
                    "StartAt": self.test_state_name,
                    "States": {
                        self.test_state_name: {
                            "PluginName": self.test_plugin_name,
                            "CmdArgsList": self.test_cmd_args_list,
                            "Timeout": None,
                            "Next": None,
                            "IsEnd": True,
                        },
                    },
                },
                "state_instances": [
                    {
                        "opawdl_state": {
                            "PluginName": self.test_plugin_name,
                            "CmdArgsList": self.test_cmd_args_list,
                            "Timeout": None,
                            "Next": None,
                            "IsEnd": True,
                        },
                        "status": "COMPLETED",
                    }
                ],
                "status": "STARTED",
            }
        )
        # Act and Assert
        self.assertEqual(
            str(self.test_opawdl_workflow_instance),
            expected_opawdl_workflow_instance_json_str,
        )
