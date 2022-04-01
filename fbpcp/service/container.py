#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
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
    def get_instance(self, instance_id: str) -> Optional[ContainerInstance]:
        """Get a specific container instance.

        Args:
            instance_id: uniquely identify a container instance.

        Returns:
            Optional - a container instance if the specified container instances was found, a None otherwise.

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
        """Cancel a running container instance.

        cancel_instance does not gurantee immediate terminations. Some implementations
        may wait for a certain grace period.
        Cancelled instance may be removed immediately, or after a short time.

        Args:
            instance_id: the instance id of the container instance to cancel.
        """
        pass

    @abc.abstractmethod
    def cancel_instances(self, instance_ids: List[str]) -> List[Optional[PcpError]]:
        """Cancel one or more running container instances.

        Args:
            instance_id: the instance ids of the container instances to cancel.

        Returns:
            A list of Optionals, in the same order as the input instance ids. A `None` indicates
            a successful cancellation, whereas a `PceError` indicates a failed cancellation and
            describes the error reason.
        """
        pass

    @abc.abstractmethod
    def get_current_instances_count(self) -> int:
        """Get total pending and running instances count for cluster
        Returns:
            Integer that represent the total pending and running instances count for cluster
        """
        pass

    @abc.abstractmethod
    def validate_container_definition(self, container_definition: str) -> None:
        """Validate the format of a specific container definition.
        Raises:
            InvalidParameterError: The container definition is not in a valid format.
        """
        pass
