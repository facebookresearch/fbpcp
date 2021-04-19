#!/usr/bin/env python3
# pyre-strict

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from dataclasses_json import dataclass_json


class VpcState(Enum):
    UNKNOWN = "UNKNOWN"
    PENDING = "PENDING"
    AVAILABLE = "AVAILABLE"


@dataclass_json
@dataclass
class Vpc:
    vpc_id: str
    state: VpcState = VpcState.UNKNOWN
    tags: Dict[str, str] = field(default_factory=lambda: {})
