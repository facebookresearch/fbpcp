#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from enum import Enum
from typing import Dict

from fbpcp.entity.cloud_provider import CloudProvider
from fbpcp.error.pcp import InvalidParameterError


class ContainerType(Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"


CONTAINER_TYPES: Dict[CloudProvider, Dict[ContainerType, Dict[str, int]]] = {
    CloudProvider.AWS: {
        ContainerType.SMALL: {"cpu": 1, "memory": 8},
        ContainerType.MEDIUM: {"cpu": 4, "memory": 30},
        ContainerType.LARGE: {"cpu": 16, "memory": 120},
    }
}


@dataclass
class ContainerTypeConfig:
    cpu: int  # Number of vCPU
    memory: int  # Memory in GB

    @classmethod
    def get_config(
        cls, cloud_provider: CloudProvider, container_type: ContainerType
    ) -> "ContainerTypeConfig":
        if cloud_provider != CloudProvider.AWS:
            raise InvalidParameterError(
                f"Cloud provider {cloud_provider} is not supported."
            )
        return cls(**CONTAINER_TYPES[cloud_provider][container_type])
