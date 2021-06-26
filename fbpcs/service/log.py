#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from typing import List

from fbpcs.entity.log_event import LogEvent


class LogService(abc.ABC):
    @abc.abstractmethod
    def fetch(self, log_path: str, start_time: int) -> List[LogEvent]:
        pass
