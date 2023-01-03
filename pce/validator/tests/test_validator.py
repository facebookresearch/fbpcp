#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import unittest

from unittest.mock import call, patch

from pce.entity.mpc_roles import MPCRoles
from pce.validator.duplicate_pce_resources_checker import DuplicatePCEResource
from pce.validator.message_templates.resource_names import ResourceNamePlural
from pce.validator.message_templates.validator_step_names import ValidationStepNames
from pce.validator.validation_suite import ValidationResult, ValidationResultCode
from pce.validator.validator import (
    get_arn,
    INCOMPATIBLE_STEP_ARG_ERROR_MESSAGE,
    main,
    OVERALL_SUCCESS_MESSAGE,
    validate_pce,
    ValidatorResult,
)

TEST_REGION = "us-west-2"
TEST_KEY_ID = "fjfj"
TEST_KEY_DATA = "ghgh"
TEST_PCE_ID = "foobar"
TEST_ROLE = MPCRoles.PUBLISHER
TEST_SKIP_STEPS = [ValidationStepNames.FIREWALL]
TEST_CLI_COMMAND = f"pce_validator --region={TEST_REGION} --pce-id={TEST_PCE_ID}"


@patch("pce.validator.validator.get_arn")
@patch("pce.validator.validator.ValidationSuite")
@patch("pce.validator.validator.AWSPCEService")
@patch("pce.validator.validator.DuplicatePCEResourcesChecker")
class TestValidatePCE(unittest.TestCase):
    def test_validate_pce_all_valid(
        self,
        MockDuplicatePCEResourcesChecker,
        MockAWSPCEService,
        MockValidationSuite,
        MockGetARN,
    ):
        # arrange
        mock_duplicate_resource_checker = MockDuplicatePCEResourcesChecker.return_value
        mock_validator = MockValidationSuite.return_value

        mock_duplicate_resource_checker.check_pce.return_value = []
        mock_validator.validate_network_and_compute.return_value = []

        # act and assert
        with self.assertLogs() as captured_logs:
            with patch("builtins.print") as mock_print:
                result = validate_pce(
                    TEST_REGION,
                    TEST_KEY_ID,
                    TEST_KEY_DATA,
                    TEST_PCE_ID,
                    TEST_ROLE,
                    TEST_SKIP_STEPS,
                    [],
                )
            mock_print.assert_called_once_with(OVERALL_SUCCESS_MESSAGE)
        # assert result set as success
        self.assertEqual(result, ValidatorResult.SUCCESS)
        # assert exactly three INFO level logs emitted
        log_records_levels = [
            log_record.levelno for log_record in captured_logs.records
        ]
        self.assertEqual(log_records_levels, [logging.INFO, logging.INFO, logging.INFO])

    def test_validate_pce_duplicate_resources_found(
        self,
        MockDuplicatePCEResourcesChecker,
        MockAWSPCEService,
        MockValidationSuite,
        MockGetARN,
    ):
        # arrange
        mock_duplicate_resource_checker = MockDuplicatePCEResourcesChecker.return_value
        mock_validator = MockValidationSuite.return_value

        # mock duplicate resource checker finding a duplicate resource
        mock_duplicate_resource_checker.check_pce.return_value = [
            DuplicatePCEResource(
                resource_name_plural=ResourceNamePlural.VPC.value,
                duplicate_resource_ids="foo, bar",
            )
        ]
        mock_validator.validate_network_and_compute.return_value = []

        # act and assert that "success" message wasn't printed
        with self.assertLogs() as captured_logs:
            with patch("builtins.print") as mock_print:
                result = validate_pce(
                    TEST_REGION,
                    TEST_KEY_ID,
                    TEST_KEY_DATA,
                    TEST_PCE_ID,
                    TEST_ROLE,
                    TEST_SKIP_STEPS,
                    [],
                )
            mock_print.assert_not_called()
        # assert result was success as ERROR
        self.assertEqual(result, ValidatorResult.ERROR)

        # assert two ERROR level logs were emitted, one describing the error
        # and second describing the duplicate resource
        log_records_levels = [
            log_record.levelno for log_record in captured_logs.records
        ]
        self.assertEqual(log_records_levels, [logging.ERROR, logging.ERROR])

    def test_validate_pce_validation_failed(
        self,
        MockDuplicatePCEResourcesChecker,
        MockAWSPCEService,
        MockValidationSuite,
        MockGetARN,
    ):
        # arrange
        mock_duplicate_resource_checker = MockDuplicatePCEResourcesChecker.return_value
        mock_validator = MockValidationSuite.return_value

        mock_duplicate_resource_checker.check_pce.return_value = []
        # mock having an error result in validation results
        mock_validator.validate_network_and_compute.return_value = [
            ValidationResult(validation_result_code=ValidationResultCode.SUCCESS),
            ValidationResult(validation_result_code=ValidationResultCode.ERROR),
        ]

        # act and assert that "success" message wasn't printed
        with self.assertLogs() as captured_logs:
            with patch("builtins.print") as mock_print:
                result = validate_pce(
                    TEST_REGION,
                    TEST_KEY_ID,
                    TEST_KEY_DATA,
                    TEST_PCE_ID,
                    TEST_ROLE,
                    TEST_SKIP_STEPS,
                    [],
                )
            mock_print.assert_not_called()
        # assert result was success as ERROR
        self.assertEqual(result, ValidatorResult.ERROR)

        # assert 3 INFO level logs were emitted indicating the validation progress,
        # followed by one ERROR level describing the overall failed validation
        log_records_levels = [
            log_record.levelno for log_record in captured_logs.records
        ]
        self.assertEqual(
            log_records_levels,
            [logging.INFO, logging.INFO, logging.INFO, logging.ERROR],
        )


@patch("sys.exit")
@patch("pce.validator.validator.validate_pce")
class TestMain(unittest.TestCase):
    def testMainErrorExitCode(self, mock_validate_pce, mock_sys_exit):
        # arrange
        mock_validate_pce.return_value = ValidatorResult.ERROR

        # act
        with patch("sys.argv", TEST_CLI_COMMAND.split()):
            main()

        # assert
        mock_sys_exit.assert_called_once_with(ValidatorResult.ERROR.value)

    def testMainSuccess(self, mock_validate_pce, mock_sys_exit):
        # arrange
        mock_validate_pce.return_value = ValidatorResult.SUCCESS

        # act
        with patch("sys.argv", TEST_CLI_COMMAND.split()):
            main()

        # assert
        mock_sys_exit.assert_called_once_with(ValidatorResult.SUCCESS.value)

    def testMainStepArgValidation(self, mock_validate_pce, mock_sys_exit):
        # arrange
        mock_validate_pce.return_value = ValidatorResult.SUCCESS
        incompatible_step_args = " --run-step=firewall --skip-step=subnets"
        test_cli_command = TEST_CLI_COMMAND + incompatible_step_args

        # act
        with patch("sys.argv", test_cli_command.split()):
            main()

        # assert
        mock_sys_exit.assert_has_calls(
            [
                call(INCOMPATIBLE_STEP_ARG_ERROR_MESSAGE),
                call(ValidatorResult.SUCCESS.value),
            ]
        )


@patch("pce.validator.validator.STSGateway")
class TestGetARN(unittest.TestCase):
    def test_get_arn(self, mockSTSGateway):
        """
        get_arn() is a simple wrapper around STSGateway.get_caller_arn() so
        this test is simply to ensure that calls have the expected input and output
        """
        # arrange
        test_arn = "arn:foo-bar"
        mock_sts_gateway_instance = mockSTSGateway.return_value
        mock_sts_gateway_instance.get_caller_arn.return_value = test_arn

        # act
        arn = get_arn(TEST_REGION, TEST_KEY_ID, TEST_KEY_DATA)

        # assert
        mockSTSGateway.assert_called_once_with(
            TEST_REGION, TEST_KEY_ID, TEST_KEY_DATA, None
        )
        mock_sts_gateway_instance.get_caller_arn.assert_called_once()
        self.assertEqual(arn, test_arn)
