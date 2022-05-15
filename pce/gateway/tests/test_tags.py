#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import TestCase
from unittest.mock import MagicMock, patch

from fbpcp.error.pcp import PcpError
from pce.gateway.tags import TagsGateway

REGION = "us-west-2"


class TestTagsGateway(TestCase):
    def setUp(self) -> None:
        self.aws_tags = MagicMock()
        with patch("boto3.client") as mock_client:
            mock_client.return_value = self.aws_tags
            self.tags = TagsGateway(REGION)

    def test_tag_resources(self) -> None:
        # Arrange
        sample_arn = "arn:aws:vpc:us-west-2:123456:vpc/vpc-1234abcd"
        sample_tags = {"tag_name": "tag_value"}
        client_return_response = {"FailedResourcesMap": {}}
        self.aws_tags.tag_resources = MagicMock(return_value=client_return_response)

        # Act
        self.tags.tag_resources([sample_arn], sample_tags)

        # Assert
        self.aws_tags.tag_resources.assert_called()

    def test_tag_resources_failure_throws(self) -> None:
        # Arrange
        sample_arn = "arn:aws:vpc:us-west-2:123456:vpc/vpc-1234abcd"
        sample_tags = {"tag_name": "tag_value"}
        client_return_response = {
            "FailedResourcesMap": {
                sample_arn: {
                    "StatusCode": 400,
                    "ErrorCode": "InvalidParameterException",
                }
            }
        }
        self.aws_tags.tag_resources = MagicMock(return_value=client_return_response)

        # Act & Assert
        self.assertRaises(
            PcpError, lambda: self.tags.tag_resources([sample_arn], sample_tags)
        )

    def test_untag_resources(self) -> None:
        # Arrange
        sample_arn = "arn:aws:vpc:us-west-2:123456:vpc/vpc-1234abcd"
        sample_tag_key = "tag_name"
        client_return_response = {"FailedResourcesMap": {}}
        self.aws_tags.untag_resources = MagicMock(return_value=client_return_response)
        # Act
        self.tags.untag_resources([sample_arn], [sample_tag_key])
        # Assert
        self.aws_tags.untag_resources.assert_called()

    def test_untag_resources_failure_throws(self) -> None:
        # Arrange
        sample_arn = "arn:aws:vpc:us-west-2:123456:vpc/vpc-1234abcd"
        sample_tag_key = "tag_name"
        client_return_response = {
            "FailedResourcesMap": {
                sample_arn: {
                    "StatusCode": 400,
                    "ErrorCode": "InvalidParameterException",
                }
            }
        }
        self.aws_tags.untag_resources = MagicMock(return_value=client_return_response)

        # Act & Assert
        self.assertRaises(
            PcpError, lambda: self.tags.untag_resources([sample_arn], [sample_tag_key])
        )

    def test_get_resources(self) -> None:
        # Arrange
        client_return_response = {
            "PaginationToken": "string",
            "ResourceTagMappingList": [
                {
                    "ResourceARN": "arn:aws:vpc:us-west-2:123456:vpc/vpc-1234abcd",
                    "Tags": [
                        {"Key": "pce-id", "Value": "1234abcd"},
                    ],
                    "ComplianceDetails": {
                        "NoncompliantKeys": [
                            "string",
                        ],
                        "KeysWithNoncompliantValues": [
                            "string",
                        ],
                        "ComplianceStatus": True,
                    },
                },
            ],
        }
        self.aws_tags.get_resources = MagicMock(return_value=client_return_response)
        expected_resource_arns = ["arn:aws:vpc:us-west-2:123456:vpc/vpc-1234abcd"]

        # Act
        resource_arns = self.tags.get_resources_for_tag("pce-id", "1234abcd")

        # Assert
        self.assertEqual(expected_resource_arns, resource_arns)
        self.aws_tags.get_resources.assert_called()
