#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import os
import signal
import subprocess
from types import FrameType
from typing import Callable, Optional


def run_cmd(
    cmd: str, timeout: Optional[int], preexec_fn: Optional[Callable[[], None]]
) -> int:
    # The handler dealing signal SIGINT, which could be Ctrl + C from user's terminal
    def _handler(signum: int, frame: Optional[FrameType]) -> None:
        raise InterruptedError

    signal.signal(signal.SIGINT, _handler)
    """
     If start_new_session is true the setsid() system call will be made in the
     child process prior to the execution of the subprocess, which makes sure
     every process in the same process group can be killed by OS if timeout occurs.
     note: setsid() will set the pgid to its pid.
    """
    with subprocess.Popen(
        cmd, shell=True, start_new_session=True, preexec_fn=preexec_fn
    ) as proc:
        try:
            proc.communicate(timeout=timeout)
        except (subprocess.TimeoutExpired, InterruptedError) as e:
            proc.terminate()
            os.killpg(proc.pid, signal.SIGTERM)
            raise e

        return proc.wait()
