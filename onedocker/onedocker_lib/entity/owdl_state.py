#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import config, DataClassJsonMixin
from onedocker.onedocker_lib.util.enforce_types import enforce_types


@enforce_types
@dataclass
class OWDLState(DataClassJsonMixin):
    type_: str = field(metadata=config(field_name="Type"))
    container_definition: str = field(metadata=config(field_name="ContainerDefinition"))
    package_name: str = field(metadata=config(field_name="PackageName"))
    cmd_args_list: List[str] = field(metadata=config(field_name="CmdArgsList"))
    timeout: Optional[int] = field(metadata=config(field_name="Timeout"), default=None)
    next_: Optional[str] = field(metadata=config(field_name="Next"), default=None)
    end: Optional[bool] = field(metadata=config(field_name="End"), default=None)
    version: Optional[str] = field(metadata=config(field_name="Version"), default=None)
    retry_count: int = field(metadata=config(field_name="RetryCount"), default=0)

    def __str__(self) -> str:
        return self.to_json()
