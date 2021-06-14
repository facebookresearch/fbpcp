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

    def __init__(
        self,
        type_: str,
        container_definition: str,
        package_name: str,
        cmd_args_list: List[str],
        timeout: Optional[int] = None,
        next_: Optional[str] = None,
        end: Optional[bool] = False,
        version: Optional[str] = None,
    ) -> None:
        self.type_ = type_
        self.container_definition = container_definition
        self.package_name = package_name
        self.cmd_args_list = cmd_args_list
        self.timeout = timeout
        self.next_ = next_
        self.end = end
        self.version = version

    def __str__(self) -> str:
        return self.to_json()
