#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from unittest.mock import patch

from onedocker.repository.onedocker_metadata_service import OneDockerMetadataService


class TestOneDockerMetadataService(unittest.TestCase):
    @patch("onedocker.repository.onedocker_metadata_service.StorageService")
    def setUp(self, mockStorageService):
        self.metadata_svc = OneDockerMetadataService(mockStorageService)

    def test_set_metadata(self):
        pass

    def test_get_metadata(self):
        pass
