#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
import re
from enum import Enum
from typing import List

from fbpcp.entity.file_information import FileInfo
from fbpcp.entity.policy_statement import PolicyStatement, PublicAccessBlockConfig


class PathType(Enum):
    Local = 1
    S3 = 2
    GCS = 3


class StorageService(abc.ABC):
    @abc.abstractmethod
    def read(self, filename: str) -> str:
        pass

    @abc.abstractmethod
    def write(self, filename: str, data: str) -> None:
        pass

    @abc.abstractmethod
    def copy(self, source: str, destination: str) -> None:
        pass

    @abc.abstractmethod
    def file_exists(self, filename: str) -> bool:
        pass

    @staticmethod
    def path_type(filename: str) -> PathType:
        s3_match = re.search(
            "^https?:/([^.]+).s3.([^.]+).amazonaws.com/(.*)$", filename
        )
        if s3_match:
            return PathType.S3

        gcs_match = re.search("^https?://storage.cloud.google.com/(.*)$", filename)
        if gcs_match:
            return PathType.GCS

        return PathType.Local

    @abc.abstractmethod
    def get_file_size(self, filename: str) -> int:
        pass

    @abc.abstractmethod
    def get_file_info(self, filename: str) -> FileInfo:
        pass

    @abc.abstractmethod
    def list_folders(self, filename: str) -> List[str]:
        pass

    @abc.abstractmethod
    def get_bucket_policy_statements(self, bucket: str) -> List[PolicyStatement]:
        pass

    @abc.abstractmethod
    def get_bucket_public_access_block(self, bucket: str) -> PublicAccessBlockConfig:
        pass
