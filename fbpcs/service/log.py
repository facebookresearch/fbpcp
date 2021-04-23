#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from typing import Any, Dict


class LogService(abc.ABC):
    @abc.abstractmethod
    def fetch(self, log_path: str) -> Dict[str, Any]:
        pass
