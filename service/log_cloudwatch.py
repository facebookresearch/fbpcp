#!/usr/bin/env python3

from typing import Any, Dict, Optional

from gateway.cloudwatch import CloudWatchGateway
from service.log import LogService


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
