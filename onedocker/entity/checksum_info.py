#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from __future__ import annotations

import base64
import json

from dataclasses import dataclass
from typing import Any, Dict, Optional, Set

from onedocker.entity.checksum_type import ChecksumType
from OpenSSL.crypto import FILETYPE_PEM, load_publickey, verify, X509


@dataclass
class ChecksumInfo:
    """
    This dataclass tracks a package's checksum info for attestation, to allow for easy comparision and tracking

    Fields:
        package_name:   String containing the package name
        version:        String containing the package version
        checksums:      Dict that holds a pairing between a ChecksumType (Key) and the corresponding hash (Value)
        Signature:      Base64 encoded string containing
    """

    package_name: str
    version: str
    checksums: Dict[str, str]
    signature: str = ""

    def __post_init__(self) -> None:
        """
        This function ensures that all checksums all follow the correct style of a ChecksumType as key to avoid any issues from occuring with invalid types being passed
        """
        for checksum in self.checksums.copy().keys():
            checksum_type = ChecksumType(checksum)
            if checksum_type in self.checksums:
                self.checksums[checksum_type.name] = self.checksums[checksum]
                del self.checksums[checksum]

    def __eq__(self, other: ChecksumInfo) -> bool:
        """
        Compares two ChecksumInfo instances in previously decided order
        1.  Compares package_name
        2.  Compares version
        3.  Checks if overlaping checkum algorithms are present
        4.  Compares overlaping checksums
        """
        # Compare package details
        if self.package_name != other.package_name:
            return False
        if self.version != other.version:
            return False

        # Common algorithms used between both instances
        algorithms = set(self.checksums) & set(other.checksums)
        if len(algorithms) == 0:
            return False
        # Compare hexdigests of matching checksum algorithms
        for algorithm in algorithms:
            if self.checksums[algorithm] != other.checksums[algorithm]:
                return False
        return True

    def asdict(self, exclude: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Returns a dict representation of all fields in ChecksumInfo

        Args:
            exclude:    Set of Strings that contains all fields to exclude from return
        """
        return (
            self.__dict__
            if not exclude
            else {
                key: self.__dict__[key] for key in self.__dict__ if key not in exclude
            }
        )

    def verify_signature(self, public_key_path: str) -> None:
        """
        Verifies data that has been recoverd allowing us to be sure that binary integrity has been maintained

        Args:
            public_key_path:    String containing filepath to public_key
        """
        # Load public key
        with open(public_key_path, "rb") as pubkey_file:
            pubkey = load_publickey(FILETYPE_PEM, pubkey_file.read())
        x509 = X509()
        x509.set_pubkey(pubkey)

        # Get signature
        signature = base64.b64decode(self.signature.encode())

        # Create a JSON copy of fields without signature field
        data = json.dumps(self.asdict(exclude={"signature"}))

        # Verify signature
        verify(x509, signature, data, "sha256")
