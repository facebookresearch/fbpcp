#!/usr/bin/env python3
# pyre-strict

import abc

from fbpcs.entity.mpc_instance import MPCInstance


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
