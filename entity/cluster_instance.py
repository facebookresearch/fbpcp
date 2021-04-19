#!/usr/bin/env python3
# pyre-strict

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from dataclasses_json import dataclass_json


class ClusterStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    UNKNOWN = "UNKNOWN"


@dataclass_json
@dataclass
class Cluster:
    cluster_arn: str
    cluster_name: str
    status: ClusterStatus = ClusterStatus.UNKNOWN
    tags: Dict[str, str] = field(default_factory=lambda: {})
