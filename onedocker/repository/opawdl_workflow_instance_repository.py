#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc

from onedocker.entity.opawdl_workflow_instance import OPAWDLWorkflowInstance


class OPAWDLWorkflowInstanceRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, instance: OPAWDLWorkflowInstance) -> None:
        pass

    @abc.abstractmethod
    def get(self, instance_id: str) -> OPAWDLWorkflowInstance:
        pass

    @abc.abstractmethod
    def update(self, instance: OPAWDLWorkflowInstance) -> None:
        pass

    @abc.abstractmethod
    def delete(self, instance_id: str) -> None:
        pass

    @abc.abstractmethod
    def exist(self, instance_id: str) -> bool:
        pass
