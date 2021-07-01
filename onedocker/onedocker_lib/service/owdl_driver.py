#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
from typing import Optional

from fbpcs.service.onedocker import OneDockerService
from onedocker.onedocker_lib.entity.owdl_state import OWDLState
from onedocker.onedocker_lib.entity.owdl_state_instance import OWDLStateInstance
from onedocker.onedocker_lib.entity.owdl_state_instance import Status as StateStatus
from onedocker.onedocker_lib.entity.owdl_workflow import OWDLWorkflow
from onedocker.onedocker_lib.entity.owdl_workflow_instance import OWDLWorkflowInstance
from onedocker.onedocker_lib.entity.owdl_workflow_instance import (
    Status as WorkflowStatus,
)


class OWDLDriver:
    """OWDLDrivingService is responsible for executing OWDLWorkflows"""

    def __init__(
        self,
        onedocker: OneDockerService,
        instance_id: str,
        owdl_workflow: Optional[OWDLWorkflow] = None,
    ) -> None:
        """Constructor of OWDLDriverService"""
        self.logger: logging.Logger = logging.getLogger(__name__)

        self.onedocker = onedocker

        if owdl_workflow is None:
            # TODO Pull from repo via instance_id
            return

        self.owdl_workflow: OWDLWorkflow = owdl_workflow
        state_instances = []
        self.owdl_workflow_instance = OWDLWorkflowInstance(
            self.owdl_workflow, state_instances, WorkflowStatus.CREATED
        )

    def _run_state(self, curr_state: OWDLState) -> None:
        container_definition = curr_state.container_definition
        package_name = curr_state.package_name
        cmd_args_list = curr_state.cmd_args_list
        timeout = curr_state.timeout

        # TODO Add versioning support to start_containers()
        container_list = self.onedocker.start_containers(
            container_definition=container_definition,
            package_name=package_name,
            cmd_args_list=cmd_args_list,
            timeout=timeout,
        )
        curr_state_instance = OWDLStateInstance(
            curr_state, container_list, StateStatus.STARTED
        )

        self.owdl_workflow_instance.add_next_state_instance(curr_state_instance)

    def start(self) -> None:
        if self.owdl_workflow_instance.status is not WorkflowStatus.CREATED:
            self.logger.error("Cannot start an already started Workflow")
            # TODO Add custom error
        else:
            curr_state = self.owdl_workflow.states[self.owdl_workflow.starts_at]
            self._run_state(curr_state)
            if self.owdl_workflow_instance.status is WorkflowStatus.CREATED:
                self.owdl_workflow_instance.status = WorkflowStatus.STARTED

    # TODO Add support for extra params
    def next(self) -> None:
        curr_state_instance = self.owdl_workflow_instance.get_current_state_instance()
        curr_state = curr_state_instance.owdl_state
        if (
            self.owdl_workflow_instance.status is not WorkflowStatus.STARTED
            or curr_state_instance.status is not StateStatus.COMPLETED
        ):
            self.logger.error(
                "Cannot go to next state of a non-terminated State or a completed Workflow"
            )
            # TODO Throw custom error
        else:
            if curr_state.end:
                self.owdl_workflow_instance.status = WorkflowStatus.COMPLETED
                self.logger.info(
                    "End was flagged as True; marking Workflow as completed"
                )
                return

            next_ = curr_state.next_
            if next_ is not None:
                curr_state = self.owdl_workflow.states[next_]

            self._run_state(curr_state)

    def cancel_state(self) -> None:
        curr_state_instance = self.owdl_workflow_instance.get_current_state_instance()
        if curr_state_instance.status is StateStatus.STARTED:
            curr_state_instance.status = StateStatus.CANCELLED
            instance_ids = [
                container.instance_id for container in curr_state_instance.containers
            ]
            self.onedocker.stop_containers(instance_ids)
        else:
            self.logger.error("Cannot cancel a state that is not STARTED")

    def retry(self) -> None:
        curr_state_instance = self.owdl_workflow_instance.get_current_state_instance()
        if curr_state_instance.status in [StateStatus.FAILED, StateStatus.CANCELLED]:
            curr_state = curr_state_instance.owdl_state
            self._run_state(curr_state)

    def is_completed(self) -> bool:
        return self.owdl_workflow_instance.status is WorkflowStatus.COMPLETED

    def cancel_workflow(self) -> None:
        self.cancel_state()
        self.owdl_workflow_instance.status = WorkflowStatus.CANCELLED
