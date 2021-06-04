#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from typing import Dict, Optional

from dataclasses_json import dataclass_json
from onedocker.onedocker_lib.entity.owdl_state import OWDLState


@dataclass_json
@dataclass
class OWDLWorkflow:
    starts_at: str
    states: Dict[str, OWDLState]
    version: Optional[str]

    def __init__(
        self, starts_at: str, states: Dict[str, OWDLState], version: Optional[str]
    ) -> None:
        self.starts_at = starts_at
        self.states = states
        self.version = version

    def __str__(self) -> str:
        # pyre-ignore
        return self.to_json()
