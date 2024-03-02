#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import json
import unittest

from fbpcp.entity.container_insight import ContainerInsight


class TestContainerInsight(unittest.TestCase):
    def setUp(self) -> None:
        self.test_time = 1674196156.00
        self.test_cluster_name = "pci-tests"
        self.test_instance_id = "a4e3bc43995f473697f7ede38699fcbe"
        self.test_status = "COMPLETED"
        self.test_exit_code = 1
        self.class_name = "ContainerInsight"

        self.test_container_insight = ContainerInsight(
            time=self.test_time,
            cluster_name=self.test_cluster_name,
            instance_id=self.test_instance_id,
            status=self.test_status,
            exit_code=self.test_exit_code,
        )

    def test_convert_to_str_with_class_name(self) -> None:
        # Arrange
        expected_str = json.dumps(
            {
                "time": self.test_time,
                "cluster_name": self.test_cluster_name,
                "instance_id": self.test_instance_id,
                "status": self.test_status,
                "exit_code": self.test_exit_code,
                "class_name": self.class_name,
            }
        )
        # Act
        actual_str = self.test_container_insight.convert_to_str_with_class_name()

        # Assert
        self.assertEqual(actual_str, expected_str)
