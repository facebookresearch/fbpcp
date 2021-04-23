#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from enum import Enum


class PathType(Enum):
    Local = 1
    S3 = 2


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
        if filename.startswith("https:"):
            return PathType.S3

        return PathType.Local
