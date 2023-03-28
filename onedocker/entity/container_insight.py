# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


from dataclasses import dataclass
from typing import Optional

from onedocker.entity.insight import Insight


@dataclass
class ContainerInsight(Insight):
    time: float
    cluster_name: str
    instance_id: str
    status: str
    exit_code: Optional[int] = None
