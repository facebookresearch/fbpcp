#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from typing import Dict, List, Optional

from fbpcp.entity.container_instance import ContainerInstance
from fbpcp.error.pcp import PcpError


class ContainerService(abc.ABC):
    @abc.abstractmethod
    def get_region(
        self,
    ) -> str:
        pass

    @abc.abstractmethod
    def get_cluster(
        self,
    ) -> str:
        pass

    @abc.abstractmethod
    def create_instance(
        self,
        container_definition: str,
        cmd: str,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> ContainerInstance:
        pass

    @abc.abstractmethod
    def create_instances(
        self,
        container_definition: str,
        cmds: List[str],
        env_vars: Optional[Dict[str, str]] = None,
    ) -> List[ContainerInstance]:
        pass

    @abc.abstractmethod
    def get_instance(self, instance_id: str) -> ContainerInstance:
        """Get a specific container instance.

        Args:
            instance_id: uniquely identify a container instance.

        Returns:
            A container instance.

        Raises:
            PcpError: The specified container instance wasn't found in the cluster.
        """
        pass

    @abc.abstractmethod
    def get_instances(
        self, instance_ids: List[str]
    ) -> List[Optional[ContainerInstance]]:
        """Get one or more container instances.

        Args:
            instance_ids: the instance ids of the container instances.

        Returns:
            A list of Optional, in the same order as the input ids. For example, if
            users pass 3 instance_ids and the second instance could not be found,
            then returned list should also have 3 elements, with the 2nd elements being None.
        """
        pass

    @abc.abstractmethod
    def cancel_instance(self, instance_id: str) -> None:
        pass

    @abc.abstractmethod
    def cancel_instances(self, instance_ids: List[str]) -> List[Optional[PcpError]]:
        pass
