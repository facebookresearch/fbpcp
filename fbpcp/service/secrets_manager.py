#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from typing import Dict, Optional

from fbpcp.entity.secret import StringSecret


class SecretsManagerService(abc.ABC):
    @abc.abstractmethod
    def create_secret(
        self, secret_name: str, secret_value: str, tags: Optional[Dict[str, str]] = None
    ) -> str:
        pass

    @abc.abstractmethod
    def get_secret(
        self,
        secret_id: str,
    ) -> StringSecret:
        pass

    @abc.abstractmethod
    async def create_secret_async(
        self, secret_name: str, secret_value: str, tags: Optional[Dict[str, str]] = None
    ) -> str:
        pass

    @abc.abstractmethod
    async def get_secret_async(
        self,
        secret_id: str,
    ) -> StringSecret:
        pass

    @abc.abstractmethod
    def delete_secret(
        self,
        secret_id: str,
    ) -> None:
        pass

    @abc.abstractmethod
    async def delete_secret_async(
        self,
        secret_id: str,
    ) -> None:
        pass
