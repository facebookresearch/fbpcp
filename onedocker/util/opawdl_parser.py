#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from onedocker.entity.opawdl_workflow import OPAWDLWorkflow


class OPAWDLParser:
    def parse_json_str_to_workflow(
        self,
        input_str: str,
    ) -> OPAWDLWorkflow:
        workflow = OPAWDLWorkflow.from_json(input_str)

        # Validate end state
        has_end = 0
        for state in workflow.states.values():
            if state.is_end:
                has_end += 1
        if has_end == 0:
            raise Exception("Input workflow string does not have an ending state.")
        elif has_end > 1:
            raise Exception(
                f"Input workflow string has multiple({has_end}) ending states."
            )

        return workflow
