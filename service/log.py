#!/usr/bin/env python3

import abc
from typing import Any, Dict


class LogService(abc.ABC):
    @abc.abstractmethod
    def fetch(self, log_path: str) -> Dict[str, Any]:
        pass
