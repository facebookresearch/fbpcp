# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""


Usage:
    pce_validator --region=<region> --pce-id=<pce_id> [--key-id=<key_id>] [--key-data=<key_data>]

Options:
    --region=<region>       (AWS) Region name
    --key-id=<key_id>       Key id
    --key-data=<key_data>   Key data
    --pce-id=<pce_id>       PCE id
"""


import logging
import sys

from docopt import docopt
from fbpcp.service.pce_aws import AWSPCEService
from pce.validator.validation_suite import (
    ValidationSuite,
)
from schema import Schema, Optional, Or


def validate_pce(region: str, key_id: str, key_data: str, pce_id: str) -> None:
    pce_service = AWSPCEService(region, key_id, key_data, None)
    logging.info(f"Loading the PCE {pce_id}...")
    pce = pce_service.get_pce(pce_id)
    logging.info(f"PCE loaded: {pce}")
    validator = ValidationSuite(region, key_id, key_data, None)

    failed_results = validator.validate_network_and_compute(pce)
    if failed_results:
        logging.error(
            f"Validation failed for PCE {pce_id}:\n{ValidationSuite.summarize_errors(failed_results)}"
        )
        if ValidationSuite.contains_error_result(failed_results):
            sys.exit(1)
    else:
        print("Your PCE environments are set up correctly.")


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    s = Schema(
        {
            "--region": str,
            "--pce-id": str,
            Optional("--key-id"): Or(None, str),
            Optional("--key-data"): Or(None, str),
        }
    )
    arguments = s.validate(docopt(__doc__))

    region = arguments["--region"]
    key_id = arguments["--key-id"]
    key_data = arguments["--key-data"]
    pce_id = arguments["--pce-id"]
    validate_pce(region, key_id, key_data, pce_id)


if __name__ == "__main__":
    main()
