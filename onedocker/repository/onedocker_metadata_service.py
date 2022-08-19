#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Dict

from fbpcp.service.storage import StorageService
from onedocker.entity.object_metadata import PackageMetadata


class OneDockerMetadataService:
    def __init__(
        self,
        storage_svc: StorageService,
    ) -> None:
        self.storage_svc = storage_svc

    def set_metadata(self, package_path: str, metadata_dict: Dict[Any, Any]) -> None:
        raise NotImplementedError

    def get_metadata(self, package_path: str) -> PackageMetadata:
        raise NotImplementedError
