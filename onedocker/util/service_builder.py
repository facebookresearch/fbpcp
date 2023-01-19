#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Dict

from fbpcp.entity.cloud_provider import CloudProvider
from fbpcp.service.storage_s3 import S3StorageService
from fbpcp.util.s3path import S3Path
from onedocker.repository.onedocker_repository_service import OneDockerRepositoryService
from onedocker.service.metadata import MetadataService

PROD = "PROD"
STAGING = "STAGING"
REPOSITORY_PATHS: Dict[str, str] = {
    PROD: "https://one-docker-repository-prod.s3.us-west-2.amazonaws.com/",
    STAGING: "https://onedocker-repository-test.s3.us-west-2.amazonaws.com/",
}

METADATA_TABLE_KEY_NAME = "primary_key"
METADATA_TABLES: Dict[str, str] = {STAGING: "metadata_test"}


def build_repository_service(
    cloud_provider: CloudProvider, env: str = "STAGING", unsigned_enabled: bool = False
) -> OneDockerRepositoryService:
    if cloud_provider != CloudProvider.AWS:
        raise NotImplementedError(
            "Only AWS is supported for building Repository Service for now."
        )
    repository_path = REPOSITORY_PATHS[env]
    region = S3Path(repository_path).region
    storage_svc = S3StorageService(
        region,
        unsigned_enabled=unsigned_enabled,
    )
    metadata_svc = MetadataService(
        region=region, table_name=METADATA_TABLES[env], key_name=METADATA_TABLE_KEY_NAME
    )
    return OneDockerRepositoryService(
        storage_svc=storage_svc,
        package_repository_path=repository_path,
        metadata_svc=metadata_svc,
    )
