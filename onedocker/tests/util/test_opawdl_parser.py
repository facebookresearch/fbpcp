#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from onedocker.entity.opawdl_state import OPAWDLState
from onedocker.entity.opawdl_workflow import OPAWDLWorkflow
from onedocker.util.opawdl_parser import OPAWDLParser


class TestOPAWDLParser(unittest.TestCase):
    def setUp(self):
        self.parser = OPAWDLParser()
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

    def test_parse_json_str_to_workflow(self):
        # Arrange
        valid_workflow = OPAWDLWorkflow(
            starts_at=self.test_state_name,
            states={self.test_state_name: self.test_opawdl_state},
        )
        # Act
        result = self.parser.parse_json_str_to_workflow(str(valid_workflow))
        # Assert
        self.assertEqual(result, valid_workflow)

    def test_parse_json_str_to_workflow_no_end(self):
        # Arrange
        test_state_no_end = self.test_opawdl_state
        test_state_no_end.is_end = False
        test_workflow_no_end = OPAWDLWorkflow(
            starts_at=self.test_state_name,
            states={self.test_state_name: test_state_no_end},
        )
        # Act and Assert
        with self.assertRaisesRegex(
            Exception,
            "Input workflow string does not have an ending state.",
        ):
            self.parser.parse_json_str_to_workflow(str(test_workflow_no_end))

    def test_parse_json_str_to_workflow_multiple_ends(self):
        # Arrange
        test_workflow_multiple_ends = OPAWDLWorkflow(
            starts_at=self.test_state_name,
            states={
                self.test_state_name: self.test_opawdl_state,
                "state_2": self.test_opawdl_state,
            },
        )
        # Act and Assert
        with self.assertRaisesRegex(
            Exception,
            "Input workflow string has multiple",
        ):
            self.parser.parse_json_str_to_workflow(str(test_workflow_multiple_ends))
