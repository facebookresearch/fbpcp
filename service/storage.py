#!/usr/bin/env python3
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
