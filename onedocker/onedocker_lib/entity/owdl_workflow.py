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
from onedocker.onedocker_lib.util.enforce_types import enforce_types


@enforce_types
@dataclass
class OWDLWorkflow(DataClassJsonMixin):
    starts_at: str = field(metadata=config(field_name="StartAt"))
    states: Dict[str, OWDLState] = field(metadata=config(field_name="States"))
    version: Optional[str] = field(metadata=config(field_name="Version"), default=None)

    def __str__(self) -> str:
        return self.to_json()
