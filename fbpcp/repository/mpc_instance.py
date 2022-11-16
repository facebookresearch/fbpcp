#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from warnings import warn

from fbpcp.entity.mpc_instance import MPCInstance


warn(
    f"{__file__} has been moved to fbpcs repo. Please consider https://github.com/facebookresearch/fbpcs/tree/main/fbpcs/private_computation/service/mpc instead.",
    DeprecationWarning,
    stacklevel=2,
)


class MPCInstanceRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, instance: MPCInstance) -> None:
        pass

    @abc.abstractmethod
    def read(self, instance_id: str) -> MPCInstance:
        pass

    @abc.abstractmethod
    def update(self, instance: MPCInstance) -> None:
        pass

    @abc.abstractmethod
    def delete(self, instance_id: str) -> None:
        pass
