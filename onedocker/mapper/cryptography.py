#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Optional

from cryptography import x509
from cryptography.x509.oid import NameOID
from fbpcp.entity.certificate_request import CertificateRequest


def map_certificaterequest_to_x509name(cert_request: CertificateRequest) -> x509.Name:
    name_list = []
    if cert_request.country_name:
        name_list.append(
            x509.NameAttribute(NameOID.COUNTRY_NAME, cert_request.country_name)
        )
    if cert_request.state_or_province_name:
        name_list.append(
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, cert_request.state_or_province_name
            )
        )
    if cert_request.locality_name:
        name_list.append(
            x509.NameAttribute(NameOID.LOCALITY_NAME, cert_request.locality_name)
        )
    if cert_request.organization_name:
        name_list.append(
            x509.NameAttribute(
                NameOID.ORGANIZATION_NAME, cert_request.organization_name
            )
        )
    if cert_request.common_name:
        name_list.append(
            x509.NameAttribute(NameOID.COMMON_NAME, cert_request.common_name)
        )

    if not name_list:
        raise Exception(
            "x509 name is empty, please add at least one x509 name attribute in CertificateRequest"
        )
    return x509.Name(name_list)


def map_certificaterequest_to_x509subjectalternativename(
    cert_request: CertificateRequest,
) -> Optional[x509.SubjectAlternativeName]:
    name_list = []
    if cert_request.dns_name:
        name_list.append(x509.DNSName(cert_request.dns_name))
    return x509.SubjectAlternativeName(name_list)
