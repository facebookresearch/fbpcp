#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


"""
CLI for running an executable in one docker


Usage:
    onedocker-runner <package_name> --cmd=<cmd> [options]

Options:
    -h --help                           Show this help
    --repository_path=<repository_path> The folder repository that the executables are to downloaded from
    --exe_path=<exe_path>               The folder that the executables are located at
    --timeout=<timeout>                 Set timeout (in sec) to task to avoid endless running
    --log_path=<path>                   Override the default path where logs are saved
    --verbose                           Set logging level to DEBUG
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Any, Optional

import psutil
import schema
from docopt import docopt
from fbpcs.service.storage_s3 import S3StorageService
from fbpcs.util.s3path import S3Path
from onedocker.common.env import ONEDOCKER_EXE_PATH, ONEDOCKER_REPOSITORY_PATH
from onedocker.common.util import run_cmd


# the folder on s3 that the executables are to downloaded from
DEFAULT_REPOSITORY_PATH = "https://one-docker-repository.s3.us-west-1.amazonaws.com/"

# the folder in the docker image that is going to host the executables
DEFAULT_EXE_FOLDER = "/root/one_docker/package/"


def run(
    repository_path: str,
    exe_path: str,
    package_name: str,
    cmd: str,
    logger: logging.Logger,
    timeout: int,
) -> None:
    # download executable from s3
    if repository_path.upper() != "LOCAL":
        logger.info("Downloading executables ...")
        _download_executables(repository_path, package_name)
    else:
        logger.info("Local repository, skip download ...")

    # grant execute permission to the downloaded executable file
    team, exe_name = _parse_package_name(package_name)
    subprocess.run(f"chmod +x {exe_path}/{exe_name}", shell=True)

    # TODO update this line after proper change in fbcode/measurement/private_measurement/pcs/oss/fbpcs/service/onedocker.py to take
    # out the hard coded exe_path in cmd string
    if repository_path.upper() == "LOCAL":
        cmd = exe_path + cmd

    # run execution cmd
    logger.info(f"Running cmd: {cmd} ...")
    net_start: Any = psutil.net_io_counters()

    return_code = run_cmd(cmd, timeout)
    if return_code != 0:
        logger.info(f"Subprocess returned non-zero return code: {return_code}")

    net_end: Any = psutil.net_io_counters()
    logger.info(
        f"Net usage: {net_end.bytes_sent - net_start.bytes_sent} bytes sent, {net_end.bytes_recv - net_start.bytes_recv} bytes received"
    )

    sys.exit(return_code)


def _download_executables(
    repository_path: str,
    package_name: str,
) -> None:
    s3_region = S3Path(repository_path).region
    team, exe_name = _parse_package_name(package_name)
    exe_local_path = DEFAULT_EXE_FOLDER + exe_name
    exe_s3_path = repository_path + package_name
    storage_svc = S3StorageService(s3_region)
    storage_svc.copy(exe_s3_path, exe_local_path)


def _parse_package_name(package_name: str) -> Tuple[str, str]:
    return package_name.split("/")[0], package_name.split("/")[1]


def _read_config(
    logger: logging.Logger,
    config_name: str,
    argument: Optional[str],
    env_var: str,
    default_val: str,
):
    if argument:
        logger.info(f"Read {config_name} from program arguments...")
        return argument

    if os.getenv(env_var):
        logger.info(f"Read {config_name} from environment variables...")
        return os.getenv(env_var)

    logger.info(f"Read {config_name} from default value...")
    return default_val


def main():
    s = schema.Schema(
        {
            "<package_name>": str,
            "--cmd": schema.Or(None, str),
            "--repository_path": schema.Or(None, schema.And(str, len)),
            "--exe_path": schema.Or(None, schema.And(str, len)),
            "--timeout": schema.Or(None, schema.Use(int)),
            "--log_path": schema.Or(None, schema.Use(Path)),
            "--verbose": bool,
            "--help": bool,
        }
    )

    arguments = s.validate(docopt(__doc__))

    log_path = arguments["--log_path"]
    log_level = logging.DEBUG if arguments["--verbose"] else logging.INFO
    logging.basicConfig(filename=log_path, level=log_level)
    logger = logging.getLogger(__name__)

    # timeout could be None if the caller did not provide the value
    timeout = arguments["--timeout"]

    repository_path = _read_config(
        logger,
        "repository_path",
        arguments["--repository_path"],
        ONEDOCKER_REPOSITORY_PATH,
        DEFAULT_REPOSITORY_PATH,
    )
    exe_path = _read_config(
        logger,
        "exe_path",
        arguments["--exe_path"],
        ONEDOCKER_EXE_PATH,
        DEFAULT_EXE_FOLDER,
    )

    logger.info("Starting program....")
    try:
        run(
            repository_path=repository_path,
            exe_path=exe_path,
            package_name=arguments["<package_name>"],
            cmd=arguments["--cmd"],
            logger=logger,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        logger.error(f"{timeout} seconds have passed. Now exiting the program....")
        sys.exit(1)
    except InterruptedError:
        logger.error("Receive abort command from user, Now exiting the program....")
        sys.exit(1)


if __name__ == "__main__":
    main()
