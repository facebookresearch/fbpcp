#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Optional

import botocore
from fbpcp.intern.gateway.aws_fb import FBAWSGateway
from pce.gateway.iam import IAMGateway


class FBPCEIAMGateway(FBAWSGateway, IAMGateway):
    def __init__(
        self,
        account: str,
        role: Optional[str] = None,
        region: Optional[str] = None,
    ) -> None:
        super().__init__(account=account, role=role, region=region)
        self.client: botocore.client.BaseClient = self.session_gen.get_client("iam")
