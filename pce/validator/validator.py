# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""


Usage:
    pce_validator --region=<region> --pce-id=<pce_id> [--key-id=<key_id>] [--key-data=<key_data>] [--role=<role>] [--run-step=<run-step> | --skip-step=<skip-step>]...

Options ([+] can be repeated):
    --region=<region>               (AWS) Region name
    --key-id=<key_id>               Key id
    --key-data=<key_data>           Key data
    --pce-id=<pce_id>               PCE id
    --role=<role>                   publisher, partner
    --run-step=<run-step> [+]       name of a validation step to be explicitly run, eg vpc_cidr
    --skip-step=<skip-step> [+]     name of a validation step to be skipped, eg vpc_peering
"""


import logging
import sys
from enum import Enum
from typing import List

from docopt import docopt
from fbpcp.service.pce_aws import AWSPCEService
from pce.entity.mpc_roles import MPCRoles
from pce.gateway.sts import STSGateway
from pce.validator.duplicate_pce_resources_checker import DuplicatePCEResourcesChecker
from pce.validator.message_templates.validator_step_names import ValidationStepNames
from pce.validator.validation_suite import ValidationSuite
from schema import And, Optional, Or, Schema, Use


# The main method in this module explicitly sets an exit code to indicate
# success or non-success of the validation, but has no further classification
# of errors and corresponding exit codes. Invalid CLI args also result in a
# exitcode of 1, either explicitly via sys.exit("message") or implicitly due
# to schema.SchemaError exception raised by schema.Schema.validate().
class ValidatorResult(Enum):
    SUCCESS = 0
    ERROR = 1


OVERALL_SUCCESS_MESSAGE = "Your PCE environments are set up correctly."
INCOMPATIBLE_STEP_ARG_ERROR_MESSAGE = (
    "Only either of --run-step or --skip-step should be provided"
)


def get_arn(
    region: str,
    key_id: str,
    key_data: str,
) -> str:

    sts_gateway: STSGateway = STSGateway(region, key_id, key_data, None)
    return sts_gateway.get_caller_arn()


def validate_pce(
    region: str,
    key_id: str,
    key_data: str,
    pce_id: str,
    role: MPCRoles,
    skip_steps: List[ValidationStepNames],
    run_steps: List[ValidationStepNames],
) -> ValidatorResult:
    duplicate_resource_checker = DuplicatePCEResourcesChecker(
        region, key_id, key_data, None
    )
    duplicate_resources = duplicate_resource_checker.check_pce(pce_id)
    if duplicate_resources:
        logging.error(
            f"Failed to load PCE due to duplicate resources tagged under same "
            "pce id. Only one each of these resources can be tagged with the "
            f"pce:pce-id ({pce_id}), and the others are mistagged. Look at "
            "other properties of these resources (like id) for a hint to the "
            "pce:pce-id the resource may correctly belong to. Details follow:"
        )
        for duplicate_resource in duplicate_resources:
            logging.error(
                f"Multiple {duplicate_resource.resource_name_plural} tagged "
                f"with pce:pce-id ({pce_id}): {duplicate_resource.duplicate_resource_ids}"
            )
        return ValidatorResult.ERROR

    pce_service = AWSPCEService(region, key_id, key_data, None)
    logging.info(f"Loading the PCE {pce_id}...")
    pce = pce_service.get_pce(pce_id)
    logging.info(f"PCE loaded: {pce}")

    arn = get_arn(region, key_id, key_data)
    logging.info(f"ARN: {arn}")

    validator = ValidationSuite(region, key_id, key_data, None, role)

    failed_results = validator.validate_network_and_compute(pce, skip_steps, run_steps)
    if failed_results:
        logging.error(
            f"Validation failed for PCE {pce_id}:\n{ValidationSuite.summarize_errors(failed_results)}"
        )
        # check if any error level results, to set overall result as ValidatorResult.ERROR
        # warning level results don't set overall result as ValidatorResult.ERROR
        if ValidationSuite.contains_error_result(failed_results):
            return ValidatorResult.ERROR
    else:
        logging.info(OVERALL_SUCCESS_MESSAGE)
    return ValidatorResult.SUCCESS


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    s = Schema(
        {
            "--region": str,
            "--pce-id": str,
            Optional("--key-id"): Or(None, str),
            Optional("--key-data"): Or(None, str),
            Optional("--role"): Or(
                None,
                And(
                    Use(str.upper),
                    lambda s: s in ("PUBLISHER", "PARTNER"),
                    Use(MPCRoles),
                ),
            ),
            Optional("--run-step"): Or(
                None,
                And(
                    list,
                    lambda step_list: all(
                        [step in ValidationStepNames.code_names() for step in step_list]
                    ),
                ),
            ),
            Optional("--skip-step"): Or(
                None,
                And(
                    list,
                    lambda step_list: all(
                        [step in ValidationStepNames.code_names() for step in step_list]
                    ),
                ),
            ),
        }
    )

    arguments = s.validate(docopt(__doc__))

    region = arguments["--region"]
    key_id = arguments["--key-id"]
    key_data = arguments["--key-data"]
    pce_id = arguments["--pce-id"]
    role = arguments["--role"]
    skip_step_code_names = arguments["--skip-step"]
    run_step_code_names = arguments["--run-step"]

    if run_step_code_names and skip_step_code_names:
        sys.exit(INCOMPATIBLE_STEP_ARG_ERROR_MESSAGE)

    skip_steps = [
        ValidationStepNames.from_code_name(code_name)
        for code_name in skip_step_code_names
    ]
    run_steps = [
        ValidationStepNames.from_code_name(code_name)
        for code_name in run_step_code_names
    ]

    result = validate_pce(region, key_id, key_data, pce_id, role, skip_steps, run_steps)
    # set program's exitcode to the value defined in the ValidatorResult enum
    sys.exit(result.value)


if __name__ == "__main__":
    main()
