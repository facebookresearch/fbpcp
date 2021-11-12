# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import List, Optional, Dict, Any

import boto3
from fbpcp.gateway.aws import AWSGateway


class EC2Gateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)

        # pyre-ignore
        self.client = boto3.client("ec2", region_name=self.region, **self.config)

    def describe_availability_zones(
        self,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        response = self.client.describe_availability_zones()

        return [aws_az["ZoneName"] for aws_az in response["AvailabilityZones"]]
