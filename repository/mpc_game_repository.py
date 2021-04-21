#!/usr/bin/env python3
# pyre-strict

import abc

from fbpcs.entity.mpc_game_config import MPCGameConfig


class MPCGameRepository(abc.ABC):
    @abc.abstractmethod
    def get_game(self, name: str) -> MPCGameConfig:
        pass
