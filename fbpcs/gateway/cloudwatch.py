#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Optional, Dict, List, Any

import boto3
from fbpcs.decorator.error_handler import error_handler
from fbpcs.entity.log_event import LogEvent
from fbpcs.gateway.aws import AWSGateway


class CloudWatchGateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)
        # pyre-ignore
        self.client = boto3.client("logs", region_name=self.region, **self.config)

    @error_handler
    def get_log_events(
        self,
        log_group: str,
        log_stream: str,
        start_time: int = 0,
    ) -> List[LogEvent]:
        events = self.client.get_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            startTime=start_time,
        )["events"]

        return [LogEvent(event["timestamp"], event["message"]) for event in events]
