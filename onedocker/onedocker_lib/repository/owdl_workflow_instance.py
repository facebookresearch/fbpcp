#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc

from onedocker.onedocker_lib.entity.owdl_workflow_instance import OWDLWorkflowInstance


class OWDLWorkflowInstanceRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, instance: OWDLWorkflowInstance) -> None:
        pass

    @abc.abstractmethod
    def read(self, instance_id: str) -> str:
        pass

    @abc.abstractmethod
    def update(self, instance: OWDLWorkflowInstance) -> None:
        pass

    @abc.abstractmethod
    def delete(self, instance_id: str) -> None:
        pass
