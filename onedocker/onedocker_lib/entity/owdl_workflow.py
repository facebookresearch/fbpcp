#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from typing import Dict, Optional

from dataclasses_json import config, DataClassJsonMixin
from onedocker.onedocker_lib.entity.owdl_state import OWDLState


@dataclass
class OWDLWorkflow(DataClassJsonMixin):
    starts_at: str = field(metadata=config(field_name="StartAt"))
    states: Dict[str, OWDLState] = field(metadata=config(field_name="States"))
    version: Optional[str] = field(metadata=config(field_name="Version"), default=None)

    def __init__(
        self, starts_at: str, states: Dict[str, OWDLState], version: Optional[str]
    ) -> None:
        self.starts_at = starts_at
        self.states = states
        self.version = version

    def __str__(self) -> str:
        return self.to_json()
