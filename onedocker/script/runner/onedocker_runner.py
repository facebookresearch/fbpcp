#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

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
    --cert_params=<cert_params>         string format of CertificateRequest dictionary if a TLS certificate is requested
    --verbose                           Set logging level to DEBUG.
"""
import logging
import os
import resource
import signal
import stat
import subprocess
import sys
from pathlib import Path
from shlex import join, split
from typing import Optional

import psutil
import schema
from docopt import docopt
from fbpcp.entity.certificate_request import CertificateRequest
from fbpcp.service.storage_s3 import S3StorageService
from fbpcp.util.s3path import S3Path
from onedocker.common.core_dump_handler_aws import AWSCoreDumpHandler
from onedocker.common.env import (
    CORE_DUMP_REPOSITORY_PATH,
    ONEDOCKER_EXE_PATH,
    ONEDOCKER_REPOSITORY_PATH,
)
from onedocker.common.util import run_cmd
from onedocker.repository.onedocker_package import OneDockerPackageRepository
from onedocker.service.certificate_self_signed import SelfSignedCertificateService


# The default OneDocker repository path on S3
DEFAULT_REPOSITORY_PATH = (
    "https://one-docker-repository-prod.s3.us-west-2.amazonaws.com/"
)

# The default path in the Docker image that is going to host the executables
DEFAULT_EXE_FOLDER = "/root/onedocker/package/"

# the default version of the binary
DEFAULT_BINARY_VERSION = "latest"

logger: logging.Logger


def _set_resource_limit() -> None:
    """Set the core file size for the child process"""
    core_size = resource.RLIM_INFINITY
    resource.setrlimit(resource.RLIMIT_CORE, (core_size, core_size))


def _prepare_executable(
    repository_path: str,
    exe_path: str,
    package_name: str,
    version: str,
) -> str:
    # download executable from s3
    if repository_path.upper() != "LOCAL":
        _download_executables(repository_path, exe_path, package_name, version)
    else:
        logger.info("Local repository, skip download ...")

    # grant execute permission to the downloaded executable file
    exe_name = _parse_package_name(package_name)

    executable = f"{exe_path}{exe_name}"
    if not os.access(executable, os.X_OK):
        os.chmod(executable, os.stat(executable).st_mode | stat.S_IEXEC)
    return executable


def _run_executable(
    executable: str, timeout: int, exe_args: Optional[str] = None
) -> None:
    # run execution cmd
    cmd = _build_cmd(executable, exe_args)
    env_core_dump_repo_path = os.getenv(CORE_DUMP_REPOSITORY_PATH)
    preexec_fn = None
    if env_core_dump_repo_path:
        # set the resource limit before run
        preexec_fn = _set_resource_limit
    else:
        logger.info(
            f"The environment variable {CORE_DUMP_REPOSITORY_PATH} is not set, the core dump handling process will be skipped."
        )

    logger.info(f"Running cmd: {cmd} ...")
    net_start = psutil.net_io_counters()

    return_code = run_cmd(cmd, timeout, preexec_fn)
    if return_code != 0:
        logger.error(f"Subprocess returned non-zero return code: {return_code}")

        # shell exit code: 128 + N
        # reference: https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html
        if return_code == signal.SIGSEGV + 128 and env_core_dump_repo_path:
            logger.info("Start to process core dump ...")

            storage_svc = S3StorageService(S3Path(env_core_dump_repo_path).region)
            core_dump_handler = AWSCoreDumpHandler(storage_svc)
            core_dump_file_path = core_dump_handler.locate_core_dump_file()

            if core_dump_file_path:
                core_dump_handler.upload_core_dump_file(
                    core_dump_file_path, env_core_dump_repo_path
                )

    net_end = psutil.net_io_counters()
    logger.info(
        f"Net usage: {net_end.bytes_sent - net_start.bytes_sent} bytes sent, {net_end.bytes_recv - net_start.bytes_recv} bytes received"
    )

    sys.exit(return_code)


def _run_package(
    repository_path: str,
    exe_path: str,
    package_name: str,
    version: str,
    timeout: int,
    exe_args: Optional[str] = None,
    certificate_request: Optional[CertificateRequest] = None,
) -> None:
    logger.info(f"Starting to run {package_name}, version: {version}")
    executable = ""

    if certificate_request:
        _generate_certificate(certificate_request, exe_path)

    try:
        executable = _prepare_executable(
            repository_path=repository_path,
            exe_path=exe_path,
            package_name=package_name,
            version=version,
        )
    except Exception as err:
        logger.exception(
            f"An error was raised while preparing {package_name}:{version} from {repository_path}, error: {err}"
        )
        sys.exit(1)

    try:
        _run_executable(
            executable=executable,
            timeout=timeout,
            exe_args=exe_args,
        )
    except subprocess.TimeoutExpired as err:
        logger.exception(
            f"{timeout} seconds have passed. Now exiting the program...\n{err}"
        )
        sys.exit(1)
    except InterruptedError as err:
        logger.exception(
            f"Receive abort command from user, Now exiting the program...\n{err}",
        )
        sys.exit(1)
    except Exception as err:
        logger.exception(
            f"An error was raised while running {package_name}, error: {err}"
        )
        sys.exit(1)


def _build_cmd(executable: str, exe_args: Optional[str]) -> str:
    args_list = split(exe_args) if exe_args else []
    args_list.insert(0, executable)
    return join(args_list)


def _download_executables(
    repository_path: str,
    executable_path: str,
    package_name: str,
    version: str,
) -> None:
    exe_name = _parse_package_name(package_name)
    exe_local_path = executable_path + exe_name
    exe_s3_path = f"{repository_path}{package_name}/{version}/{exe_name}"
    storage_svc = S3StorageService(S3Path(repository_path).region)
    onedocker_package_repository = OneDockerPackageRepository(
        storage_svc, repository_path
    )
    logger.info(f"Downloading package {package_name}: {version} from {exe_s3_path}")
    onedocker_package_repository.download(package_name, version, exe_local_path)


def _parse_package_name(package_name: str) -> str:
    # Some existing packages are like private_lift/lift, so we have to split it by slash
    return package_name.split("/")[-1]


def _read_config(
    config_name: str,
    argument: Optional[str],
    env_var: str,
    default_val: str,
) -> str:
    if argument:
        logger.info(f"Read {config_name} from program arguments...")
        return argument

    env_val = os.getenv(env_var)
    if env_val:
        logger.info(f"Read {config_name} from environment variables...")
        return env_val

    logger.info(f"Read {config_name} from default value...")
    return default_val


def _generate_certificate(
    certificate_request: CertificateRequest, exe_path: str
) -> Optional[str]:
    try:
        logger.info("generating certificate")
        cert_svc = SelfSignedCertificateService(certificate_request, exe_path)
        return cert_svc.generate_certificate()

    except Exception as err:
        logger.exception(
            f"An error was raised while generating certificate for CertificateRequest {certificate_request}: {err}"
        )
        sys.exit(1)


def main() -> None:
    global logger
    s = schema.Schema(
        {
            "<package_name>": str,
            "--version": str,
            "--repository_path": schema.Or(None, schema.And(str, len)),
            "--exe_path": schema.Or(None, schema.And(str, len)),
            "--exe_args": schema.Or(None, schema.And(str, len)),
            "--timeout": schema.Or(None, schema.Use(int)),
            "--log_path": schema.Or(None, schema.Use(Path)),
            "--cert_params": schema.Or(None, schema.And(str, len)),
            "--verbose": bool,
            "--help": bool,
        }
    )

    arguments = s.validate(docopt(__doc__))

    logger = logging.getLogger(__name__)
    log_path = arguments["--log_path"]
    log_level = logging.DEBUG if arguments["--verbose"] else logging.INFO
    logging.basicConfig(filename=log_path, level=log_level)

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
    certificate_request = (
        CertificateRequest.create_instance(arguments["--cert_params"])
        if arguments["--cert_params"]
        else None
    )
    _run_package(
        repository_path=repository_path,
        exe_path=exe_path,
        package_name=arguments["<package_name>"],
        version=arguments["--version"],
        timeout=arguments["--timeout"],
        exe_args=arguments["--exe_args"],
        certificate_request=certificate_request,
    )


if __name__ == "__main__":
    main()
