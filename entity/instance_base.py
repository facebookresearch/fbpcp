#!/usr/bin/env python3
# pyre-strict

import abc


class InstanceBase(abc.ABC):
    @abc.abstractmethod
    def get_instance_id(self) -> str:
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass
