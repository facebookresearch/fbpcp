#!/usr/bin/env python3
# pyre-strict

from typing import Any, Dict, Optional

import boto3


class CloudWatchGateway:
    def __init__(
        self,
        region: str = "us-west-1",
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.region = region
        config = config or {}

        if access_key_id:
            config["aws_access_key_id"] = access_key_id

        if access_key_data:
            config["aws_secret_access_key"] = access_key_data

        # pyre-ignore
        self.client = boto3.client("logs", region_name=self.region, **config)

    def get_log_events(self, log_group: str, log_stream: str) -> Dict[str, Any]:
        return self.client.get_log_events(
            logGroupName=log_group, logStreamName=log_stream
        )
