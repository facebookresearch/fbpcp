#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
from typing import Any, Dict, Optional, Tuple

from fbpcs.entity.mpc_game_config import MPCGameConfig
from fbpcs.entity.mpc_instance import MPCRole
from fbpcs.repository.mpc_game_repository import MPCGameRepository
from fbpcs.util.arg_builder import build_cmd_args

LIFT_GAME_NAME = "lift"
LIFT_AGGREGATOR_GAME_NAME = "aggregator"


class MPCGameService:
    def __init__(self, mpc_game_repository: MPCGameRepository) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.mpc_game_repository: MPCGameRepository = mpc_game_repository

    # returns package_name and cmd which includes only arguments (no executable)
    def build_onedocker_args(
        self,
        game_name: str,
        mpc_role: MPCRole,
        server_ip: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: object,
    ) -> Tuple[str, str]:
        mpc_game_config = self.mpc_game_repository.get_game(game_name)
        return (
            mpc_game_config.onedocker_package_name,
            self._build_cmd(
                mpc_game_config=mpc_game_config,
                mpc_role=mpc_role,
                server_ip=server_ip,
                port=port,
                **kwargs,
            ),
        )

    # returns cmd which includes only arguments (no executable)
    def _build_cmd(
        self,
        mpc_game_config: MPCGameConfig,
        mpc_role: MPCRole,
        server_ip: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: object,
    ) -> str:
        args = self._prepare_args(
            mpc_game_config=mpc_game_config,
            mpc_role=mpc_role,
            server_ip=server_ip,
            port=port,
            **kwargs,
        )
        return build_cmd_args(**args)

    def _prepare_args(
        self,
        mpc_game_config: MPCGameConfig,
        mpc_role: MPCRole,
        server_ip: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs: object,
    ) -> Dict[str, Any]:
        all_arguments: Dict[str, Any] = {}

        # push MPC required arguments to dict all_arguments
        is_lift_game = (
            mpc_game_config.game_name == LIFT_AGGREGATOR_GAME_NAME
            or mpc_game_config.game_name == LIFT_GAME_NAME
        )  # TODO: T88044929 remove "role" and only support "party" for lift games
        role_or_party_key = "role" if is_lift_game else "party"
        all_arguments[role_or_party_key] = 1 if mpc_role == MPCRole.SERVER else 2

        if mpc_role == MPCRole.CLIENT:
            if server_ip is None:
                raise ValueError("Client must provide a server ip address.")
            all_arguments["server_ip"] = server_ip
        if port is not None:
            all_arguments["port"] = port

        # push game specific arguments to dict all_arguments
        for argument in mpc_game_config.arguments:
            key = argument.name
            value = kwargs.get(key)
            if value is None and argument.required:
                # Have to make game_name a special case for PL-Worker
                if key == "game_name":
                    all_arguments[key] = mpc_game_config.game_name
                else:
                    raise ValueError(f"Missing required argument {key}!")
            if value is not None:
                all_arguments[key] = value

        return all_arguments
