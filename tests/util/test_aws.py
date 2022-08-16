#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from fbpcp.error.pcp import InvalidParameterError

from fbpcp.util.aws import (
    convert_dict_to_list,
    convert_list_to_dict,
    is_container_definition_valid,
    prepare_tags,
    split_container_definition,
)

TEST_DICT = {"k1": "v1", "k2": "v2"}
TEST_LIST = [{"Name": "k1", "Value": "v1"}, {"Name": "k2", "Value": "v2"}]


class TestAWSUtil(unittest.TestCase):
    def test_convert_dict_to_list(self):
        expected_list = [
            {"Name": "k1", "Values": ["v1"]},
            {"Name": "k2", "Values": ["v2"]},
        ]
        self.assertEqual(
            expected_list, convert_dict_to_list(TEST_DICT, "Name", "Values")
        )
        self.assertEqual([], convert_dict_to_list({}, "Name", "Values"))

    def test_convert_list_dict(self):
        self.assertEqual(TEST_DICT, convert_list_to_dict(TEST_LIST, "Name", "Value"))

    def test_prepare_tags(self):
        expected_tags = {"tag:k1": "v1", "tag:k2": "v2"}
        self.assertEqual(expected_tags, prepare_tags(TEST_DICT))

    def test_is_container_definition_valid_true(self):
        # Arrange
        valid_container_definitions = [
            "pl-task-fake-business:2#pl-container-fake-business",
            "arn:aws:ecs:us-west-2:123456789012:task-definition/onedocker-task-shared-us-west-2:1#onedocker-container-shared-us-west-2",
        ]

        # Act and Assert
        for container_definition in valid_container_definitions:
            self.assertTrue(is_container_definition_valid(container_definition))

    def test_is_container_definition_valid_false(self):
        # Arrange
        invalid_container_definitions = [
            "pl-task-fake-business:2#",
            "pl-task-fake-business:2##pl-container-fake-business",
            "pl-task-fake-business#pl-container-fake-business",
            "pl-container-fake-business",
        ]

        # Act and Assert
        for container_definition in invalid_container_definitions:
            self.assertFalse(is_container_definition_valid(container_definition))

    def test_split_container_definition_throw(self):
        # Arrange
        invalid_container_definition = "pl-task-fake-business:2#"

        # Act & Assert
        with self.assertRaises(InvalidParameterError):
            split_container_definition(invalid_container_definition)

    def test_split_container_definition(self):
        # Arrange
        valid_container_definition = (
            "pl-task-fake-business:2#pl-container-fake-business"
        )

        # Act & Assert
        self.assertEqual(
            ("pl-task-fake-business:2", "pl-container-fake-business"),
            split_container_definition(valid_container_definition),
        )
