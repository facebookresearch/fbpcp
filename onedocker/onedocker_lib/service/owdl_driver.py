#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
from typing import List, Optional

from fbpcs.entity.container_instance import (
    ContainerInstance,
    ContainerInstanceStatus,
)
from fbpcs.error.owdl import OWDLRuntimeError
from fbpcs.service.onedocker import OneDockerService
from onedocker.onedocker_lib.entity.owdl_state import OWDLState
from onedocker.onedocker_lib.entity.owdl_state_instance import OWDLStateInstance
from onedocker.onedocker_lib.entity.owdl_state_instance import Status as StateStatus
from onedocker.onedocker_lib.entity.owdl_workflow import OWDLWorkflow
from onedocker.onedocker_lib.entity.owdl_workflow_instance import OWDLWorkflowInstance
from onedocker.onedocker_lib.entity.owdl_workflow_instance import (
    Status as WorkflowStatus,
)
from onedocker.onedocker_lib.repository.owdl_workflow_instance_local import (
    LocalOWDLWorkflowInstanceRepository,
)
from onedocker.onedocker_lib.util.enforce_types import enforce_types


@enforce_types
class OWDLDriver:
    """OWDLDrivingService is responsible for executing OWDLWorkflows"""

    def __init__(
        self,
        onedocker: OneDockerService,
        instance_id: str,
        repo: LocalOWDLWorkflowInstanceRepository,
        owdl_workflow: Optional[OWDLWorkflow] = None,
    ) -> None:
        """Constructor of OWDLDriverService"""
        self.logger: logging.Logger = logging.getLogger(__name__)

        self.onedocker = onedocker

        if owdl_workflow is None:
            # if repo is not None:
            #     self.owdl_workflow_instance: OWDLWorkflowInstance = (
            #         OWDLWorkflowInstance.loads_schema(
            #             json.dumps(repo.read(instance_id))
            #         )
            #     )
            #     self.owdl_workflow: OWDLWorkflow = (
            #         self.owdl_workflow_instance.owdl_workflow
            #     )
            # else:
            #     self.logger.error("Need either a workflow or a repo")
            #     return
            return
        else:
            self.owdl_workflow: OWDLWorkflow = owdl_workflow
            state_instances = []
            self.owdl_workflow_instance: OWDLWorkflowInstance = OWDLWorkflowInstance(
                instance_id, self.owdl_workflow, state_instances, WorkflowStatus.CREATED
            )
            repo.create(self.owdl_workflow_instance)

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

        self._add_next_state_instance(curr_state_instance)

    def start(self) -> None:
        if self.owdl_workflow_instance.status is not WorkflowStatus.CREATED:
            self.logger.error(
                f"Cannot start a Workflow that is started, failed or cancelled, the current Workflow is {self.owdl_workflow_instance.status}"
            )
            raise OWDLRuntimeError("Invalid status while starting the Workflow")
        curr_state = self.owdl_workflow.states[self.owdl_workflow.starts_at]
        self._run_state(curr_state)
        if self.owdl_workflow_instance.status is WorkflowStatus.CREATED:
            self.owdl_workflow_instance.status = WorkflowStatus.STARTED

    # TODO Add support for extra params
    def next(self) -> None:
        curr_state_instance = self._get_current_state_instance()
        curr_state = curr_state_instance.owdl_state
        if (
            self.owdl_workflow_instance.status is not WorkflowStatus.STARTED
            or curr_state_instance.status is not StateStatus.COMPLETED
        ):
            self.logger.error(
                f"Cannot go to next state of a non-terminated State or a completed Workflow; the current Workflow status is {self.owdl_workflow_instance.status} and the current State status is {curr_state_instance.status}"
            )
            raise OWDLRuntimeError(
                "Invalid status while attempting to run next state of Workflow"
            )
        if curr_state.end:
            self.owdl_workflow_instance.status = WorkflowStatus.COMPLETED
            self.logger.info("End was flagged as True; marking Workflow as completed")
            return

        next_ = curr_state.next_
        if next_ is not None:
            curr_state = self.owdl_workflow.states[next_]

        self._run_state(curr_state)

    def get_status(self) -> OWDLWorkflowInstance:
        if self.owdl_workflow_instance.status in [
            WorkflowStatus.CREATED,
            WorkflowStatus.COMPLETED,
        ]:
            return self.owdl_workflow_instance

        curr_state_instance = self._get_current_state_instance()
        if curr_state_instance.status is StateStatus.CANCELLED:
            return self.owdl_workflow_instance

        instance_ids = [
            container.instance_id
            for container in self._get_current_state_instance().containers
        ]

        self._get_current_state_instance().containers = self.onedocker.get_containers(
            instance_ids
        )

        status = self._get_state_status(curr_state_instance.containers)
        self._get_current_state_instance().status = status

        self.owdl_workflow_instance.status = self._get_workflow_status(status)

        return self.owdl_workflow_instance

    def cancel_state(self) -> None:
        if self.owdl_workflow_instance.status is not WorkflowStatus.STARTED:
            self.logger.error(
                f"Cannot cancel a State in a Workflow that is not STARTED; the current status is {self.owdl_workflow_instance.status}"
            )
            raise OWDLRuntimeError("Invalid Workflow status for cancelling State")

        curr_state_instance = self._get_current_state_instance()
        if curr_state_instance.status is not StateStatus.STARTED:
            self.logger.error(
                f"Cannot cancel a State that is not STARTED; the current status is {curr_state_instance.status}"
            )
            raise OWDLRuntimeError("Invalid State status for cancelling State")
        else:
            curr_state_instance.status = StateStatus.CANCELLED
            instance_ids = [
                container.instance_id for container in curr_state_instance.containers
            ]
            self.onedocker.stop_containers(instance_ids)

    def retry(self) -> None:
        if self.owdl_workflow_instance.status is WorkflowStatus.CREATED:
            self.logger.error(
                f"Cannot retry a State in a Workflow that has not STARTED; the current Workflow status is {self.owdl_workflow_instance.status}"
            )
            raise OWDLRuntimeError("Invalid Workflow status for retry")
        curr_state_instance = self._get_current_state_instance()
        if curr_state_instance.status in [StateStatus.FAILED, StateStatus.CANCELLED]:
            curr_state_instance.status = StateStatus.STARTED
            curr_state = curr_state_instance.owdl_state
            self._run_state(curr_state)

    def is_completed(self) -> bool:
        return self.owdl_workflow_instance.status is WorkflowStatus.COMPLETED

    def cancel_workflow(self) -> None:
        self.cancel_state()
        self.owdl_workflow_instance.status = WorkflowStatus.CANCELLED

    def _get_state_status(self, containers: List[ContainerInstance]) -> StateStatus:
        has_started = False
        for container in containers:
            if container.status in [
                ContainerInstanceStatus.STARTED,
                ContainerInstanceStatus.UNKNOWN,
            ]:
                has_started = True
            elif container.status is ContainerInstanceStatus.FAILED:
                return StateStatus.FAILED
        if has_started:
            return StateStatus.STARTED
        return StateStatus.COMPLETED

    def _get_workflow_status(self, status: StateStatus) -> WorkflowStatus:
        if status is StateStatus.FAILED:
            return WorkflowStatus.FAILED
        elif status is StateStatus.CANCELLED:
            return WorkflowStatus.CANCELLED
        else:
            return self.owdl_workflow_instance.status

    def _get_current_state_instance(self) -> OWDLStateInstance:
        if not self.owdl_workflow_instance.state_instances:
            raise OWDLRuntimeError(
                "Cannot get state instance of a Workflow that has not started any state instances"
            )
        return self.owdl_workflow_instance.state_instances[-1]

    def _add_next_state_instance(self, state_inst: OWDLStateInstance) -> None:
        self.owdl_workflow_instance.state_instances.append(state_inst)
