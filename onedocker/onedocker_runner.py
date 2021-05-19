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
import signal
import subprocess
import sys
from pathlib import Path
from typing import Tuple

import psutil
import schema
from docopt import docopt
from fbpcs.service.storage_s3 import S3StorageService
from fbpcs.util.s3path import S3Path


# the folder in the docker image that is going to host the executables
DEFAULT_EXE_FOLDER = "/root/one_docker/package/"
# the folder on s3 that the executables are to downloaded from
DEFAULT_REPOSITORY_PATH = "https://one-docker-repository.s3.us-west-1.amazonaws.com/"


# The handler dealing signal SIGINT, which could be Ctrl + C from user's terminal
def handler(signum, frame):
    raise InterruptedError


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
    signal.signal(signal.SIGINT, handler)
    """
     If start_new_session is true the setsid() system call will be made in the
     child process prior to the execution of the subprocess, which makes sure
     every process in the same process group can be killed by OS if timeout occurs.
     note: setsid() will set the pgid to its pid.
    """
    with subprocess.Popen(cmd, shell=True, start_new_session=True) as proc:
        net_start = psutil.net_io_counters()
        try:
            proc.communicate(timeout=timeout)
        except (subprocess.TimeoutExpired, InterruptedError) as e:
            proc.terminate()
            os.killpg(proc.pid, signal.SIGTERM)
            raise e

        return_code = proc.wait()
        net_end = psutil.net_io_counters()
        logger.info(
            f"Net usage: {net_end.bytes_sent - net_start.bytes_sent} bytes sent, {net_end.bytes_recv - net_start.bytes_recv} bytes received"
        )
        if return_code != 0:
            logger.info(f"Subprocess returned non-zero return code: {return_code}")
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

    repository_path = arguments["--repository_path"]
    if repository_path:
        logger.info("Read repository path from program arguments...")
    else:
        repository_path = os.getenv("REPOSITORY_PATH", "").strip()
        if repository_path:
            logger.info("Read repository path from environment variables...")
        else:
            repository_path = DEFAULT_REPOSITORY_PATH
            logger.info("Read repository path from default value...")

    exe_path = arguments["--exe_path"]
    if exe_path:
        logger.info("exe folder path from program arguments...")
    else:
        exe_path = os.getenv("ONEDOCKER_EXE_PATH", "").strip()
        if exe_path:
            logger.info("exe folder path from environment variables...")
        else:
            exe_path = DEFAULT_EXE_FOLDER
            logger.info("Read repository path from default value...")

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
