#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from docopt import docopt
from onedocker.script.cli.onedocker_cli import __doc__ as __onedocker_cli_doc__


class TestOnedockerCli(unittest.TestCase):
    def setUp(self):
        self.package_name = "foo"
        self.package_dir = "test/bar/"
        self.version = "baz"
        self.config_file = "test_config_file.yml"
        self.timeout = "100"
        self.cmd_args = "-h"
        self.container = "secret_container"
        self.base_args = {
            "upload": False,
            "test": False,
            "show": False,
            "stop": False,
            "--help": False,
            "--verbose": False,
            "--enable_attestation": False,
            "--package_name": None,
            "--version": None,
            "--package_dir": None,
            "--config": None,
            "--log_path": None,
            "--cmd_args": None,
            "--timeout": None,
            "--container": None,
        }

    def test_docopt_args_upload(self):
        # Arrange
        doc = __onedocker_cli_doc__

        expected_args = self.base_args
        expected_args.update(
            {
                "upload": True,
                "--enable_attestation": True,
                "--package_name": self.package_name,
                "--version": self.version,
                "--package_dir": self.package_dir,
                "--config": self.config_file,
            }
        )

        # Act
        args = docopt(
            doc,
            [
                "upload",
                "--enable_attestation",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--package_dir=" + self.package_dir,
                "--version=" + self.version,
            ],
        )

        # Assert
        self.assertDictEqual(expected_args, args)

    def test_docopt_args_test(self):
        # Arrange
        doc = __onedocker_cli_doc__

        expected_args = self.base_args
        expected_args.update(
            {
                "test": True,
                "--config": self.config_file,
                "--package_name": self.package_name,
                "--cmd_args": self.cmd_args,
                "--timeout": self.timeout,
            }
        )

        # Act
        args = docopt(
            doc,
            [
                "test",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
                "--cmd_args=" + self.cmd_args,
                "--timeout=" + self.timeout,
            ],
        )

        # Assert
        self.assertDictEqual(expected_args, args)

    def test_docopt_args_show(self):
        # Arrange
        doc = __onedocker_cli_doc__

        expected_args = self.base_args
        expected_args.update(
            {
                "show": True,
                "--config": self.config_file,
                "--package_name": self.package_name,
            }
        )

        # Act
        args = docopt(
            doc,
            [
                "show",
                "--config=" + self.config_file,
                "--package_name=" + self.package_name,
            ],
        )

        # Assert
        self.assertDictEqual(expected_args, args)

    def test_docopt_args_stop(self):
        # Arrange
        doc = __onedocker_cli_doc__

        expected_args = self.base_args
        expected_args.update(
            {
                "stop": True,
                "--config": self.config_file,
                "--container": self.container,
            }
        )

        # Act
        args = docopt(
            doc,
            [
                "stop",
                "--config=" + self.config_file,
                "--container=" + self.container,
            ],
        )

        # Assert
        self.assertDictEqual(expected_args, args)
