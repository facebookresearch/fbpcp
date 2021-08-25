#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


from functools import reduce
from typing import Dict, List


def convert_dict_to_list(
    target_dict: Dict[str, str], key: str, value: str
) -> List[Dict[str, List[str]]]:
    """
    Input examples:
        target_dict: {"k1": "v1", "k2": "v2"}
        key: "Name",
        value: "Values"
    Output examples:
        [
            {"Name": "k1", "Values": ["v1"]},
            {"Name": "k2", "Values": ["v2"]},
        ]
    """
    return reduce(
        lambda x, y: [*x, {key: y, value: [target_dict[y]]}], target_dict.keys(), []
    )


def convert_list_to_dict(
    target_list: List[Dict[str, str]], key: str, value: str
) -> Dict[str, str]:
    """
    Input examples:
        target_list:
        [
            {"Name": "k1", "Values": "v1"},
            {"Name": "k2", "Values": "v2"},
        ]
        key: "Name",
        value: "Value"
    Output examples: {"k1": "v1", "k2": "v2"}
    """
    return reduce(lambda x, y: {**x, **{y[key]: y[value]}}, target_list, {})


def prepare_tags(tags: Dict[str, str]) -> Dict[str, str]:
    """
    Input examples: {"k1": "v1", "k2": "v2"}
    Output examples: {"tag:k1": "v1", "tag:k2", "v2"}
    """
    return reduce(lambda x, y: {**x, **{f"tag:{y}": tags[y]}}, tags.keys(), {})
