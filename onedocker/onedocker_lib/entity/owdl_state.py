#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class OWDLState:
    type_: str
    container_definition: str
    package_name: str
    cmd_args_list: List[str]
    timeout: Optional[int]
    next_: Optional[str]
    end: Optional[bool]
    version: Optional[str]

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
        # pyre-ignore
        return self.to_json()
