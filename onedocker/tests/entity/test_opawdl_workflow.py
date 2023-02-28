#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import unittest

from onedocker.entity.opawdl_state import OPAWDLState
from onedocker.entity.opawdl_workflow import OPAWDLWorkflow


class TestOPAWDLWorkflow(unittest.TestCase):
    def setUp(self) -> None:
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

    def test__str__(self) -> None:
        # Arrange
        expected_opawdl_workflow_json_str = json.dumps(
            {
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
            }
        )
        # Act and Assert
        self.assertEqual(
            str(self.test_opawdl_workflow), expected_opawdl_workflow_json_str
        )
