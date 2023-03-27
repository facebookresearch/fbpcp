#!/usr/bin/env fbpython
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import unittest
from typing import List, Optional

from unittest.mock import call, MagicMock, patch

from tls.tls_cert_installer import DEFAULT_REGION, main


class TestTlsCertInstaller(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.server_cert_content = "test_server_certificate"
        self.server_cert_path = "test_server_certificate_path"
        self.issuer_cert_content = "test_issuer_certificate"
        self.issuer_cert_path = "test_issuer_certificate_path"
        self.private_key_content = "test_private_key"
        self.private_key_path = "test_private_key_path"
        self.home_dir = "/home/onedocker"
        self.ip_address = "10.0.0.0"
        self.server_uri = "study0.pc.facebook.com"
        self.private_key_ref = "test_private_key_ref"

    @patch("tls.tls_cert_installer._write_content_to_file")
    @patch("tls.tls_cert_installer.os.getenv")
    def test_main_publisher_side(
        self, mock_get_env_vars: MagicMock, mock_write: MagicMock
    ) -> None:
        # Arrange
        mock_get_env_vars.side_effect = self._get_env_vars_in_the_order_of_being_called(
            server_cert_content=self.server_cert_content,
            server_cert_path=self.server_cert_path,
            issuer_cert_content=self.issuer_cert_content,
            issuer_cert_path=self.issuer_cert_path,
            private_key_content=self.private_key_content,
            private_key_path=self.private_key_path,
            home_dir=self.home_dir,
        )
        full_server_cert_path = os.path.join(self.home_dir, self.server_cert_path)
        full_issuer_cert_path = os.path.join(self.home_dir, self.issuer_cert_path)
        full_private_key_path = os.path.join(self.home_dir, self.private_key_path)

        # Act
        main()

        # Assert
        mock_write.assert_has_calls(
            [
                call(full_server_cert_path, self.server_cert_content),
                call(full_issuer_cert_path, self.issuer_cert_content),
                call(full_private_key_path, self.private_key_content),
            ]
        )

    @patch("tls.tls_cert_installer.os.system")
    @patch("tls.tls_cert_installer._write_content_to_file")
    @patch("tls.tls_cert_installer.os.getenv")
    def test_main_partner_side(
        self,
        mock_get_env_vars: MagicMock,
        mock_write: MagicMock,
        mock_os_system: MagicMock,
    ) -> None:
        # Arrange
        mock_get_env_vars.side_effect = self._get_env_vars_in_the_order_of_being_called(
            issuer_cert_content=self.issuer_cert_content,
            issuer_cert_path=self.issuer_cert_path,
            home_dir=self.home_dir,
            ip_address=self.ip_address,
            server_uri=self.server_uri,
        )
        full_issuer_cert_path = os.path.join(self.home_dir, self.issuer_cert_path)

        # Act
        main()

        # Assert
        mock_write.assert_called_once_with(
            full_issuer_cert_path, self.issuer_cert_content
        )
        mock_os_system.assert_called_once_with(
            f"sudo /home/onedocker/package/write_routing.sh {self.ip_address} {self.server_uri}"
        )

    @patch("tls.tls_cert_installer._get_secret")
    @patch("tls.tls_cert_installer._write_content_to_file")
    @patch("tls.tls_cert_installer.os.getenv")
    def test_main_with_secret(
        self,
        mock_get_env_vars: MagicMock,
        mock_write: MagicMock,
        mock_get_secret: MagicMock,
    ) -> None:
        # Arrange
        secret_value = "test_secret_value"
        mock_get_secret.return_value = secret_value
        mock_get_env_vars.side_effect = self._get_env_vars_in_the_order_of_being_called(
            private_key_ref=self.private_key_ref,
            private_key_path=self.private_key_path,
            home_dir=self.home_dir,
        )
        full_private_key_path = os.path.join(self.home_dir, self.private_key_path)

        # Act
        main()

        # Assert
        mock_get_secret.assert_called_once_with(self.private_key_ref, DEFAULT_REGION)
        mock_write.assert_called_with(full_private_key_path, secret_value)

    def _get_env_vars_in_the_order_of_being_called(
        self,
        server_cert_content: Optional[str] = None,
        server_cert_path: Optional[str] = None,
        issuer_cert_content: Optional[str] = None,
        issuer_cert_path: Optional[str] = None,
        private_key_content: Optional[str] = None,
        private_key_ref: Optional[str] = None,
        private_key_path: Optional[str] = None,
        home_dir: Optional[str] = None,
        ip_address: Optional[str] = None,
        server_uri: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[Optional[str]]:
        return [
            server_cert_content,
            server_cert_path,
            issuer_cert_content,
            issuer_cert_path,
            private_key_content,
            private_key_ref,
            private_key_path,
            home_dir,
            ip_address,
            server_uri,
            region,
        ]
