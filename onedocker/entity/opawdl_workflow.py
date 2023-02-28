#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from typing import Dict

from dataclasses_json import config, DataClassJsonMixin

from onedocker.entity.opawdl_state import OPAWDLState


@dataclass
class OPAWDLWorkflow(DataClassJsonMixin):
    starts_at: str = field(metadata=config(field_name="StartAt"))
    states: Dict[str, OPAWDLState] = field(metadata=config(field_name="States"))

    def __str__(self) -> str:
        return self.to_json()
