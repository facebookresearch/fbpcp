#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
import subprocess
from typing import List

from onedocker.entity.opawdl_state import OPAWDLState
from onedocker.entity.opawdl_state_instance import (
    OPAWDLStateInstance,
    Status as StateStatus,
)

from onedocker.entity.opawdl_workflow import OPAWDLWorkflow
from onedocker.entity.opawdl_workflow_instance import (
    OPAWDLWorkflowInstance,
    Status as WorkflowStatus,
)
from onedocker.repository.opawdl_workflow_instance_repository import (
    OPAWDLWorkflowInstanceRepository,
)
from onedocker.util.opawdl_parser import OPAWDLParser


class OPAWDLDriver:
    """OPAWDLDriver Executes OPAWDL Workflow"""

    def __init__(
        self,
        instance_id: str,
        workflow_path: str,
        repo: OPAWDLWorkflowInstanceRepository,
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.workflow_instance_id = instance_id
        self.workflow_instance_repo = repo
        with open(workflow_path, "r") as f:
            parser = OPAWDLParser()
            self.workflow: OPAWDLWorkflow = parser.parse_json_str_to_workflow(f.read())
        # initialize workflow instance
        self.workflow_instance: OPAWDLWorkflowInstance = OPAWDLWorkflowInstance(
            instance_id=self.workflow_instance_id,
            opawdl_workflow=self.workflow,
            state_instances=[],
            status=WorkflowStatus.CREATED,
        )
        self.workflow_instance_repo.create(self.workflow_instance)

    def run_workflow(self) -> None:
        self.logger.info(f"Running workflow: {self.workflow_instance_id}")
        curr_state_name = self.workflow.starts_at
        curr_state = self.workflow.states[self.workflow.starts_at]

        while curr_state is not None:
            # run current state
            self.logger.info(f"Running state: {curr_state_name}")
            self._run_state(curr_state)
            # find next state
            if curr_state.next_ is not None and curr_state.is_end is False:
                curr_state_name = curr_state.next_
                curr_state = self.workflow.states[curr_state.next_]
            else:
                curr_state = None

        self.workflow_instance.status = WorkflowStatus.COMPLETED
        self.workflow_instance_repo.update(self.workflow_instance)
        self.logger.info(f"Workflow {self.workflow_instance_id} completed running")

    def _run_state(self, curr_state: OPAWDLState) -> None:
        curr_state_instance = OPAWDLStateInstance(curr_state, StateStatus.STARTED)

        # execute cmd
        shell_cmd = self._build_shell_cmd(
            plugin_name=curr_state.plugin_name, cmd_args_list=curr_state.cmd_args_list
        )
        subprocess.run(shell_cmd, shell=True)

        # update instances
        curr_state_instance = OPAWDLStateInstance(curr_state, StateStatus.COMPLETED)
        self._add_state_instance_to_workflow_instance(curr_state_instance)

    def _build_shell_cmd(self, plugin_name: str, cmd_args_list: List[str]) -> str:
        return plugin_name + " " + " ".join(cmd_args_list)

    def _add_state_instance_to_workflow_instance(
        self, state_instance: OPAWDLStateInstance
    ) -> None:
        self.workflow_instance.state_instances.append(state_instance)
        self.workflow_instance_repo.update(self.workflow_instance)
