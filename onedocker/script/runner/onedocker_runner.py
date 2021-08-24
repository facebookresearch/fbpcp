#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


"""
CLI for running an executable in OneDocker containers.


Usage:
    onedocker-runner <package_name> --version=<version> [options]

Options:
    -h --help                           Show this help
    --repository_path=<repository_path> OneDocker repository path where the executables are downloaded from. No download when "LOCAL" repository is specified.
    --exe_path=<exe_path>               The local path where the executables are downloaded to.
    --exe_args=<exe_args>               The arguments the executable will use.
    --timeout=<timeout>                 Set timeout (in sec) to kill the task.
    --log_path=<path>                   Override the default path where logs are saved.
    --verbose                           Set logging level to DEBUG.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from shlex import join, split
from typing import Any, Optional

import psutil
import schema
from docopt import docopt
from fbpcp.service.storage_s3 import S3StorageService
from fbpcp.util.s3path import S3Path
from onedocker.common.env import ONEDOCKER_EXE_PATH, ONEDOCKER_REPOSITORY_PATH
from onedocker.common.util import run_cmd


# The default OneDocker repository path on S3
DEFAULT_REPOSITORY_PATH = (
    "https://one-docker-repository-prod.s3.us-west-2.amazonaws.com/"
)

# The default path in the Docker image that is going to host the executables
DEFAULT_EXE_FOLDER = "/root/onedocker/package/"

# the default version of the binary
DEFAULT_BINARY_VERSION = "latest"


def _run_package(
    repository_path: str,
    exe_path: str,
    package_name: str,
    version: str,
    timeout: int,
    exe_args: Optional[str] = None,
) -> None:
    logger = logging.getLogger(__name__)
    # download executable from s3
    if repository_path.upper() != "LOCAL":
        _download_executables(repository_path, package_name, version)
    else:
        logger.info("Local repository, skip download ...")

    # grant execute permission to the downloaded executable file
    exe_name = _parse_package_name(package_name)

    executable = f"{exe_path}{exe_name}"
    os.chmod(executable, 0o755)

    # run execution cmd
    cmd = _build_cmd(executable, exe_args)
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


def _build_cmd(executable: str, exe_args: Optional[str]) -> str:
    args_list = split(exe_args) if exe_args else []
    args_list.insert(0, executable)
    return join(args_list)


def _download_executables(
    repository_path: str,
    package_name: str,
    version: str,
) -> None:
    logger = logging.getLogger(__name__)
    s3_region = S3Path(repository_path).region
    _, exe_name = _parse_package_name(package_name)
    # TODO: Remove the hard coded path
    exe_local_path = DEFAULT_EXE_FOLDER + exe_name
    exe_s3_path = f"{repository_path}{package_name}/{version}/{exe_name}"
    logger.info(f"Downloading executables from {exe_s3_path}")
    storage_svc = S3StorageService(s3_region)
    storage_svc.copy(exe_s3_path, exe_local_path)


def _parse_package_name(package_name: str) -> str:
    # Some existing packages are like private_lift/lift, so we have to split it by slash
    package = package_name.split("/")
    return package[len(package) - 1]


def _read_config(
    config_name: str,
    argument: Optional[str],
    env_var: str,
    default_val: str,
):
    logger = logging.getLogger(__name__)
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
            "--version": str,
            "--repository_path": schema.Or(None, schema.And(str, len)),
            "--exe_path": schema.Or(None, schema.And(str, len)),
            "--exe_args": schema.Or(None, schema.Use(str, len)),
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
        "repository_path",
        arguments["--repository_path"],
        ONEDOCKER_REPOSITORY_PATH,
        DEFAULT_REPOSITORY_PATH,
    )
    exe_path = _read_config(
        "exe_path",
        arguments["--exe_path"],
        ONEDOCKER_EXE_PATH,
        DEFAULT_EXE_FOLDER,
    )

    logger.info("Starting program....")
    try:
        _run_package(
            repository_path=repository_path,
            exe_path=exe_path,
            package_name=arguments["<package_name>"],
            version=arguments["--version"],
            timeout=timeout,
            exe_args=arguments["--exe_args"],
        )
    except subprocess.TimeoutExpired:
        logger.error(f"{timeout} seconds have passed. Now exiting the program....")
        sys.exit(1)
    except InterruptedError:
        logger.error("Receive abort command from user, Now exiting the program....")
        sys.exit(1)


if __name__ == "__main__":
    main()
