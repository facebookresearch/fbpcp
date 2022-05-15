#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import TestCase
from unittest.mock import MagicMock, patch

from pce.gateway.ecs import ECSGateway


class TestECSGateway(TestCase):
    REGION = "us-west-1"
    TEST_LOG_GROUP = "ecs/test-log-group-name"
    TEST_TASK_ARN = (
        "arn:aws:ecs:us-west-1:123456789012:task-definition/test-definition:1"
    )
    TEST_CONTAINER_ID = f"{TEST_TASK_ARN}#test-container"

    @patch("boto3.client")
    def setUp(self, mock_boto_client: MagicMock) -> None:
        self.aws_ecs = MagicMock()
        mock_boto_client.return_value = self.aws_ecs
        self.ecs = ECSGateway(region=self.REGION)

    def test_extract_log_group_name(self) -> None:
        # Arrange
        test_definition_response = {
            "taskDefinition": {
                "taskDefinitionArn": self.TEST_TASK_ARN,
                "containerDefinitions": [
                    # the following container parameters are listed in https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html
                    {
                        "name": "test-container",
                        "image": "test-image:latest",
                        "cpu": 4096,
                        "memory": 30720,
                        "portMappings": [],
                        "essential": "true",
                        "entryPoint": ["sh", "-c"],
                        "environment": [],
                        "mountPoints": [],
                        "volumesFrom": [],
                        "logConfiguration": {
                            "logDriver": "awslogs",
                            "options": {
                                "awslogs-group": self.TEST_LOG_GROUP,
                                "awslogs-region": self.REGION,
                                "awslogs-stream-prefix": "ecs",
                            },
                        },
                    }
                ],
            }
        }

        self.aws_ecs.describe_task_definition = MagicMock(
            return_value=test_definition_response
        )

        # Act
        log_group_name = self.ecs.extract_log_group_name(
            container_definition_id=self.TEST_CONTAINER_ID
        )

        # Assert
        self.assertEqual(log_group_name, self.TEST_LOG_GROUP)
        self.aws_ecs.describe_task_definition.assert_called()

    def test_extract_nonexist_log_group_name(self) -> None:
        # Arrange
        test_definition__no_log_response = {
            "taskDefinition": {
                "taskDefinitionArn": self.TEST_TASK_ARN,
                "containerDefinitions": [
                    {
                        "name": "test-container",
                        "image": "test-image:latest",
                        "cpu": 4096,
                        "memory": 30720,
                        "portMappings": [],
                        "essential": "true",
                        "entryPoint": ["sh", "-c"],
                        "environment": [],
                        "mountPoints": [],
                        "volumesFrom": [],
                        "logConfiguration": {},
                    }
                ],
            }
        }

        self.aws_ecs.describe_task_definition = MagicMock(
            return_value=test_definition__no_log_response
        )

        # Act
        log_group_name = self.ecs.extract_log_group_name(
            container_definition_id=self.TEST_CONTAINER_ID
        )

        # Assert
        self.assertIsNone(log_group_name, "log group is None")
        self.aws_ecs.describe_task_definition.assert_called()
