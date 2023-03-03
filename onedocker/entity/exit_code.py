#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from enum import IntEnum


class ExitCode(IntEnum):
    """Custom exit codes for OneDocker containers.

    Unix uses error codes above 125 specially for failures, so they should be avoided for program errors.

    The meaning of the codes is approximately as follows:
        SUCCESS -- The program succeeded.
        EXE_ERROR -- The executable itself exited with non-zero code.
        ERROR -- Catchall for general errors.
        SERVICE_UNAVAILABLE -- A service is unavailable. This can occur if a support program or file is unavailable.
        TIMEOUT -- The program timed out.
        SIGINT -- The program received SIGINT signal.

    For other exit codes please refer to https://man.freebsd.org/cgi/man.cgi?sysexits.
    """

    SUCCESS = 0
    EXE_ERROR = 1
    ERROR = 64
    SERVICE_UNAVAILABLE = 69
    TIMEOUT = 124
    SIGINT = 130
