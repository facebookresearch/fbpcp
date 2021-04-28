#!/usr/bin/env python3


"""
CLI for running an executable in one docker


Usage:
    one-docker-runner --package_name=<package_name> --cmd=<cmd> [options]

Options:
    -h --help                           Show this help
    --repository_path=<repository_path> The folder repository that the executables are to downloaded from
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

import schema
from docopt import docopt
from fbpcs.service.storage_s3 import S3StorageService
from fbpcs.util.s3path import S3Path


# the folder in the docker image that is going to host the executables
EXE_FOLDER = "/root/one_docker/package/"
# the folder on s3 that the executables are to downloaded from
REPOSITORY_PATH = "https://one-docker-repository.s3.us-west-1.amazonaws.com/"


# The handler dealing signal SIGINT, which could be Ctrl + C from user's terminal
def handler(signum, frame):
    raise InterruptedError


def run(
    repository_path: str,
    package_name: str,
    cmd: str,
    logger: logging.Logger,
    timeout: int,
) -> None:
    # download executable from s3
    logger.info("Downloading executables ...")
    _download_executables(repository_path, package_name)

    # grant execute permission to the downloaded executable file
    team, exe_name = _parse_package_name(package_name)
    subprocess.run(f"chmod +x {EXE_FOLDER}/{exe_name}", shell=True)

    # run execution cmd
    logger.info(f"Running cmd: {cmd} ...")
    signal.signal(signal.SIGINT, handler)
    """
     If start_new_session is true the setsid() system call will be made in the
     child process prior to the execution of the subprocess, which makes sure
     every process in the same process group can be killed by OS if timeout occurs.
     note: setsid() will set the pgid to its pid.
    """
    with subprocess.Popen(cmd, shell=True, start_new_session=True) as process:
        try:
            process.communicate(timeout=timeout)
        except (subprocess.TimeoutExpired, InterruptedError) as e:
            process.terminate()
            os.killpg(process.pid, signal.SIGTERM)
            raise e
    return_code = process.wait()
    if return_code != 0:
        logger.info(f"subprocess returned non-zero return code: {return_code}")
        sys.exit(return_code)


def _download_executables(
    repository_path: str,
    package_name: str,
) -> None:
    s3_region = S3Path(repository_path).region
    team, exe_name = _parse_package_name(package_name)
    exe_local_path = EXE_FOLDER + exe_name
    exe_s3_path = repository_path + package_name
    storage_svc = S3StorageService(s3_region)
    storage_svc.copy(exe_s3_path, exe_local_path)


def _parse_package_name(package_name: str) -> Tuple[str, str]:
    return package_name.split("/")[0], package_name.split("/")[1]


def main():
    s = schema.Schema(
        {
            "--package_name": schema.Or(None, str),
            "--cmd": schema.Or(None, str),
            "--repository_path": schema.Or(None, str),
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
    if repository_path is not None and repository_path.strip():
        logger.info("Read repository path from program arguments...")
    else:
        repository_path = os.getenv("REPOSITORY_PATH")
        if repository_path is not None and repository_path.strip():
            logger.info("Read repository path from environment variables...")
        else:
            repository_path = REPOSITORY_PATH
            logger.info("Read repository path from default value...")

    logger.info("Starting container....")
    try:
        run(
            repository_path=repository_path,
            package_name=arguments["--package_name"],
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
