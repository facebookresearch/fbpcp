#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from fbpcp.entity.secret import StringSecret

from fbpcp.service.secrets_manager_aws import AWSSecretsManagerService


class TestAWSSecretsManagerService(unittest.TestCase):
    @patch("fbpcp.gateway.secrets_manager.AWSSecretsManagerGateway")
    def setUp(self, MockSMGateway):
        self.region = "us-west-2"
        self.secret_svc = AWSSecretsManagerService(region=self.region)
        self.secret_svc.secret_gateway = MockSMGateway()

    def test_create_secret(self):
        # Arrange
        secret_name = "name"
        secret_value = "value"
        tags = {"key": "value"}
        expected_response = "secret_id"
        self.secret_svc.secret_gateway.create_secret.return_value = expected_response

        # Act
        resp = self.secret_svc.create_secret(secret_name, secret_value, tags)

        # Assert
        self.secret_svc.secret_gateway.create_secret.assert_called_with(
            secret_name=secret_name, secret_value=secret_value, tags=tags
        )
        self.assertEqual(resp, expected_response)

    def test_get_secret(self):
        # Arrange
        secret_id = "secret_id"
        expected_response = StringSecret(
            id=secret_id, name="test", value="test", create_date="03-08-2023"
        )
        self.secret_svc.secret_gateway.get_secret.return_value = expected_response

        # Act
        resp = self.secret_svc.get_secret(secret_id)

        # Assert
        self.assertEqual(resp, expected_response)
        self.secret_svc.secret_gateway.get_secret.assert_called_with(
            secret_id=secret_id
        )

    def test_delete_secret(self):
        # Arrange
        secret_id = "secret_id"

        # Act
        self.secret_svc.delete_secret(secret_id)

        # Assert
        self.secret_svc.secret_gateway.delete_secret.assert_called_with(
            secret_id=secret_id
        )


class TestAWSSecretsManagerServiceAsync(IsolatedAsyncioTestCase):
    @patch("fbpcp.gateway.secrets_manager.AWSSecretsManagerGateway")
    def setUp(self, MockSMGateway):
        self.region = "us-west-2"
        self.secret_svc = AWSSecretsManagerService(region=self.region)
        self.secret_svc.secret_gateway = MockSMGateway()
        self.secret_name = "name"
        self.secret_value = "value"
        self.secret_id = "test_id"
        self.tags = {"key": "value"}

    @patch("fbpcp.service.secrets_manager_aws.AWSSecretsManagerService.create_secret")
    async def test_create_secret_async(self, create_secret_mock):
        # Act
        await self.secret_svc.create_secret_async(
            self.secret_name, self.secret_value, self.tags
        )

        # Assert
        create_secret_mock.assert_called_with(
            self.secret_name, self.secret_value, self.tags
        )

    @patch("fbpcp.service.secrets_manager_aws.AWSSecretsManagerService.get_secret")
    async def test_get_secret_async(self, get_secret_mock):
        # Act
        await self.secret_svc.get_secret_async(self.secret_id)

        # Assert
        get_secret_mock.assert_called_with(self.secret_id)

    @patch("fbpcp.service.secrets_manager_aws.AWSSecretsManagerService.delete_secret")
    async def test_delete_secret_async(self, delete_secret_mock):
        # Act
        await self.secret_svc.delete_secret_async(self.secret_id)

        # Assert
        delete_secret_mock.assert_called_with(self.secret_id)
