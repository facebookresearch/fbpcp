#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
from typing import Any, Dict, Optional


class AWSGateway:
    def __init__(
        self,
        region: Optional[str] = None,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        session_token: Optional[str] = None,
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.region = region
        self.config: Dict[str, Any] = config or {}

        if access_key_id is not None:
            self.config["aws_access_key_id"] = access_key_id

        if access_key_data is not None:
            self.config["aws_secret_access_key"] = access_key_data

        if session_token is not None:
            self.config["aws_session_token"] = session_token
