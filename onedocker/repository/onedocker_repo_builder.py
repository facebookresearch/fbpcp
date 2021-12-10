#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from fbpcp.error.pcp import PcpError
from fbpcp.service.storage import StorageService, PathType
from fbpcp.service.storage_gcs import GCSStorageService
from fbpcp.service.storage_s3 import S3StorageService
from fbpcp.util.s3path import S3Path
from onedocker.repository.onedocker_package import OneDockerPackageRepository


class OneDockerPackageRepositoryBuilder:
    # This builder (subject to change) is for supporting multi-cloud in onedocker_runner, which uses the container credentials. (Task role in AWS and workload identity in GCP)
    @classmethod
    def create_repository(
        cls,
        repository_path: str,
    ) -> OneDockerPackageRepository:
        repo_path_type = StorageService.path_type(repository_path)
        if repo_path_type != PathType.S3 and repo_path_type != PathType.GCS:
            raise PcpError(f"{repo_path_type.name} repository is not supported yet")

        if repo_path_type == PathType.S3:
            s3_storage_svc = S3StorageService(S3Path(repository_path).region)
            return OneDockerPackageRepository(s3_storage_svc, repository_path)
        else:
            gcs_storage_svc = GCSStorageService()
            return OneDockerPackageRepository(gcs_storage_svc, repository_path)
