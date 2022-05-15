#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import json
from dataclasses import dataclass, fields
from enum import Enum
from typing import List, Optional

from fbpcp.error.pcp import InvalidParameterError


class KeyAlgorithm(Enum):
    # For now we only support RSA since it is one of the most common algorithms, will add more key algorithms in the future
    RSA = "RSA"

    @classmethod
    def has_member(cls, name: str) -> bool:
        return name in cls.__members__


@dataclass
class CertificateRequest:
    key_algorithm: KeyAlgorithm
    key_size: int
    passphrase: str
    cert_folder: Optional[str]
    private_key_name: Optional[str]
    certificate_name: Optional[str]
    days_valid: Optional[int]
    country_name: Optional[str]
    state_or_province_name: Optional[str]
    locality_name: Optional[str]
    organization_name: Optional[str]
    common_name: Optional[str]
    dns_name: Optional[str]

    @classmethod
    def get_non_optional_fields(cls) -> List[str]:
        fields_list = fields(cls)
        return [
            field.name for field in fields_list if field.type != Optional[field.type]
        ]

    @classmethod
    def create_instance(cls, cert_params: str) -> "CertificateRequest":
        try:
            cert_params_dict = json.loads(cert_params)
        except Exception as err:
            raise InvalidParameterError(
                f"An error was raised when unpack cert_params for CertificateRequest {cert_params}: {err}"
            )
        required_keys = set(cls.get_non_optional_fields())
        if not required_keys.issubset(set(cert_params_dict.keys())):
            raise InvalidParameterError(
                f"One of the required parameters {required_keys} is missing in cert_params: {cert_params_dict.keys()}"
            )
        key_algorithm_str = cert_params_dict["key_algorithm"]
        if not KeyAlgorithm.has_member(key_algorithm_str):
            raise InvalidParameterError(
                f"key_algorithm {key_algorithm_str} is not supported"
            )

        return cls(
            key_algorithm=KeyAlgorithm[key_algorithm_str],
            key_size=int(cert_params_dict["key_size"]),
            passphrase=cert_params_dict["passphrase"],
            cert_folder=cert_params_dict.get("cert_folder", None),
            private_key_name=cert_params_dict.get("private_key_name", None),
            certificate_name=cert_params_dict.get("certificate_name", None),
            days_valid=cert_params_dict.get("days_valid", None),
            country_name=cert_params_dict.get("country_name", None),
            state_or_province_name=cert_params_dict.get("state_or_province_name", None),
            locality_name=cert_params_dict.get("locality_name", None),
            organization_name=cert_params_dict.get("organization_name", None),
            common_name=cert_params_dict.get("common_name", None),
            dns_name=cert_params_dict.get("dns_name", None),
        )

    def convert_to_cert_params(self) -> str:
        cert_dict = {}
        for f in fields(self.__class__):
            fname = f.name
            fvalue = getattr(self, f.name)
            if fname == "key_algorithm":
                cert_dict[fname] = fvalue.value
            elif fvalue is not None:
                cert_dict[fname] = fvalue

        return json.dumps(cert_dict)
