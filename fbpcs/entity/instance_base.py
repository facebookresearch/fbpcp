#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc


class InstanceBase(abc.ABC):
    @abc.abstractmethod
    def get_instance_id(self) -> str:
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass
