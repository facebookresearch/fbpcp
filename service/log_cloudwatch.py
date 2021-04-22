#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, Optional

from fbpcs.gateway.cloudwatch import CloudWatchGateway
from fbpcs.service.log import LogService


class CloudWatchLogService(LogService):
    def __init__(
        self,
        log_group: str,
        region: str = "us-west-1",
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.cloudwatch_gateway = CloudWatchGateway(
            region, access_key_id, access_key_data, config
        )
        self.log_group = log_group

    def fetch(self, log_path: str) -> Dict[str, Any]:
        """Fetch logs"""
        return self.cloudwatch_gateway.get_log_events(self.log_group, log_path)
