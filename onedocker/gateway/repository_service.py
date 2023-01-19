#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Dict

from fbpcp.entity.cloud_provider import CloudProvider
from onedocker.repository.onedocker_repository_service import OneDockerRepositoryService

from onedocker.util.service_builder import build_repository_service


class RepositoryServiceGateway:
    def __init__(self) -> None:
        self.repository_service: OneDockerRepositoryService = build_repository_service(
            cloud_provider=CloudProvider.AWS
        )

    def get_measurements(self, package_name: str, version: str) -> Dict[str, str]:
        return self.repository_service.get_package_measurements(package_name, version)
