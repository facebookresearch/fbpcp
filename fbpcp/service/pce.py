#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc

from fbpcp.entity.pce import PCE


class PCEService(abc.ABC):
    @abc.abstractmethod
    def get_pce(
        self,
        pce_id: str,
    ) -> PCE:
        pass
