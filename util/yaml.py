#!/usr/bin/env python3
# pyre-strict

from pathlib import Path
from typing import Any, Dict

import yaml


def load(file_path: Path) -> Dict[str, Any]:
    with open(file_path) as stream:
        return yaml.safe_load(stream)


# pyre-ignore
def dump(data: Any, file_path: Path) -> None:
    with open(file_path, "w") as f:
        return yaml.dump(data, f)
