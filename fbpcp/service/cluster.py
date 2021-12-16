#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from typing import List

from fbpcp.entity.cluster_instance import Cluster
from fbpcp.entity.container_instance import ContainerInstance

# API's to discover clusters and container instances in a region
class ClusterService(abc.ABC):
    @abc.abstractmethod
    def get_region(
        self,
    ) -> str:
        pass

    @abc.abstractmethod
    def list_clusters(
        self,
    ) -> List[Cluster]:
        pass

    @abc.abstractmethod
    def list_instances(
        self,
        cluster_name: str,
    ) -> List[ContainerInstance]:
        pass
