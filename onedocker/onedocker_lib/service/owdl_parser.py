#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging

from onedocker.onedocker_lib.entity.owdl_workflow import OWDLWorkflow


class OWDLParserService:
    """OWDLParserService is responsible for parsing JSON files into OWDLWorkflows"""

    def __init__(self) -> None:
        """Constructor of OWDLParserService"""
        self.logger: logging.Logger = logging.getLogger(__name__)

    def parse(
        self,
        input_str: str,
    ) -> OWDLWorkflow:

        workflow = OWDLWorkflow.from_json(input_str)  # pyre-ignore

        return workflow
