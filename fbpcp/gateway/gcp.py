#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import json
import logging
from typing import Any, Dict, Optional


class GCPGateway:
    def __init__(
        self,
        credentials_json: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.config: Dict[str, Any] = config or {}

        if credentials_json is not None:
            self.config["credentials_json"] = json.loads(credentials_json)
