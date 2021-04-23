#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc

from fbpcs.entity.mpc_game_config import MPCGameConfig


class MPCGameRepository(abc.ABC):
    @abc.abstractmethod
    def get_game(self, name: str) -> MPCGameConfig:
        pass
