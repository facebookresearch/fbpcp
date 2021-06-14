#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import unittest
from typing import Any, Dict

from fbpcs.error.owdl import OWDLParsingError
from onedocker.onedocker_lib.service.owdl_parser import OWDLParserService


class ParserTestUtil(unittest.TestCase):
    def setUp(self):
        self.parser = OWDLParserService()

    @staticmethod
    def _remove_none_json(input_dict: Dict[str, Any]) -> Dict[str, Any]:
        for k in list(input_dict.keys()):
            v = input_dict[k]
            if isinstance(v, dict):
                ParserTestUtil._remove_none_json(v)
            elif v is None:
                input_dict.pop(k)
                continue

        return input_dict

    def test_parse_incorrectly_formatted_input(self):
        input_str = """
            StartAt: Calculate
            States:
            Calculate:
                Type: Task
                ContainerDefinition: xx
                PackageName: yy
                CmdArgsList:
                - aa
                - bb
                - cc
                Timeout: 100
                Next: Aggregate
            Aggregate:
                Type: Task
                ContainerDefinition: xx
                PackageName: yy
                CmdArgsList:
                - aa
                - bb
                - cc
                Timeout: 0
                End: true
            """
        self.assertRaises(
            json.decoder.JSONDecodeError,
            self.parser.parse,
            input_str,
        )

    def test_parse_missing_args(self):
        input_str = {
            "States": {
                "Calculate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 100,
                    "Next": "Aggregate",
                },
                "Aggregate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 0,
                    "End": True,
                },
            }
        }

        self.assertRaises(
            KeyError,
            self.parser.parse,
            json.dumps(input_str),
        )

    def test_parse_states_missing_args(self):
        input_str = {
            "StartAt": "Calculate",
            "States": {
                "Calculate": {
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 100,
                    "Next": "Aggregate",
                },
                "Aggregate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "Timeout": 0,
                    "End": True,
                },
            },
        }

        self.assertRaises(
            KeyError,
            self.parser.parse,
            json.dumps(input_str),
        )

    def test_parse_bad_value(self):
        input_str = {
            "StartAt": 12,
            "States": {
                "Calculate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 100,
                    "Next": "Aggregate",
                },
                "Aggregate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 0,
                    "End": True,
                },
            },
        }

        self.assertRaises(
            OWDLParsingError,
            self.parser.parse,
            json.dumps(input_str),
        )

    def test_parse_bad_value_state(self):
        input_str = {
            "StartAt": "Calculate",
            "States": {
                "Calculate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": "1z00",
                    "Next": "Aggregate",
                },
                "Aggregate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 0,
                    "End": True,
                },
            },
        }

        self.assertRaises(
            OWDLParsingError,
            self.parser.parse,
            json.dumps(input_str),
        )

    def test_parse_bad_value_state_2(self):
        input_str = {
            "StartAt": "Calculate",
            "States": {
                "Calculate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": "100",
                    "Next": "Aggregate",
                },
                "Aggregate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 0,
                    "End": True,
                },
            },
        }

        self.assertRaises(
            OWDLParsingError,
            self.parser.parse,
            json.dumps(input_str),
        )

    def test_parse_bad_value_state_3(self):
        input_str = {
            "StartAt": "Calculate",
            "States": {
                "Calculate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 100,
                    "Next": "Aggregate",
                },
                "Aggregate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 0,
                    "End": "true",
                },
            },
        }

        self.assertRaises(
            OWDLParsingError,
            self.parser.parse,
            json.dumps(input_str),
        )

    def test_parse_missing_key(self):
        input_str = {
            "States": {
                "Calculate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 100,
                    "Next": "Aggregate",
                },
                "Aggregate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 0,
                    "End": True,
                },
            },
        }

        self.assertRaises(
            KeyError,
            self.parser.parse,
            json.dumps(input_str),
        )

    def test_parse_missing_key_2(self):
        input_str = {
            "StartAt": "Calculate",
            "State": {
                "Calculate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 100,
                    "Next": "Aggregate",
                },
                "Aggregate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 0,
                    "End": True,
                },
            },
        }

        self.assertRaises(
            KeyError,
            self.parser.parse,
            json.dumps(input_str),
        )

    # def test_no_end(self):
    #     parser = OWDLParserService()
    #     input_str = {
    #         "StartAt": "Calculate",
    #         "States": {
    #             "Calculate": {
    #                 "Type": "Task",
    #                 "ContainerDefinition": "xx",
    #                 "PackageName": "yy",
    #                 "CmdArgsList": ["aa", "bb", "cc"],
    #                 "Timeout": 100,
    #                 "Next": "Aggregate",
    #             },
    #             "Aggregate": {
    #                 "Type": "Task",
    #                 "ContainerDefinition": "xx",
    #                 "PackageName": "yy",
    #                 "CmdArgsList": ["aa", "bb", "cc"],
    #                 "Timeout": 0,
    #             },
    #         },
    #     }

    #     self.assertRaises(
    #         Exception,
    #         self.parser.parse,
    #         json.dumps(input_str),
    #     )

    def test_general_parse(self):
        input_str = {
            "StartAt": "Calculate",
            "States": {
                "Calculate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 100,
                    "Next": "Aggregate",
                },
                "Aggregate": {
                    "Type": "Task",
                    "ContainerDefinition": "xx",
                    "PackageName": "yy",
                    "CmdArgsList": ["aa", "bb", "cc"],
                    "Timeout": 0,
                    "End": True,
                },
            },
        }

        self.maxDiff = None
        self.assertEqual(
            json.dumps(
                self._remove_none_json(
                    input_dict=json.loads(str(self.parser.parse(json.dumps(input_str))))
                )
            ),
            json.dumps(input_str),
        )
