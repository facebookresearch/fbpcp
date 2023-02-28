#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import config, DataClassJsonMixin


@dataclass
class OPAWDLState(DataClassJsonMixin):
    plugin_name: str = field(metadata=config(field_name="PluginName"))
    cmd_args_list: List[str] = field(metadata=config(field_name="CmdArgsList"))
    timeout: Optional[int] = field(metadata=config(field_name="Timeout"), default=None)
    next_: Optional[str] = field(metadata=config(field_name="Next"), default=None)
    is_end: Optional[bool] = field(metadata=config(field_name="IsEnd"), default=True)

    def __str__(self) -> str:
        return self.to_json()
