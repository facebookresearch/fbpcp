#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


from functools import reduce
from typing import Any, Dict, List, Optional, Tuple, Union


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
    if target_list is not None:
        return reduce(lambda x, y: {**x, **{y[key]: y[value]}}, target_list, {})
    else:
        return {}


# pyre-ignore
def convert_obj_to_list(obj: Any) -> List:
    return obj if isinstance(obj, list) else [obj]


def get_json_values(json_elem: Union[str, Dict[str, Any]]) -> List[str]:
    """
    Input examples: {"k1": ["v1", "v2"], "k2": "v3"}
    Output examples: ["v1", "v2", "v3"]
    """
    if isinstance(json_elem, str):
        return [json_elem]
    ret = []
    for val in json_elem.values():
        ret.extend(convert_obj_to_list(val))
    return ret


def prepare_tags(tags: Dict[str, str]) -> Dict[str, str]:
    """
    Input examples: {"k1": "v1", "k2": "v2"}
    Output examples: {"tag:k1": "v1", "tag:k2", "v2"}
    """
    return reduce(lambda x, y: {**x, **{f"tag:{y}": tags[y]}}, tags.keys(), {})


def convert_vpc_tags_to_filter(
    tags: Optional[Dict[str, str]] = None, vpc_id: Optional[str] = None
) -> List[Dict[str, List[str]]]:
    """
    Input examples:
        tags [Optional]: {"k1": "v1", "k2": "v2"},
        vpc_id [Optional]: "vpc-id-ex"
    Output examples:
        [
            {"Name": "k1", "Values": ["v1"]},
            {"Name": "k2", "Values": ["v2"]},
            {"Name": "vpc-id", "Values": ["vpc-id-ex"]}
        ]
    """
    vpc_dict = {"vpc-id": vpc_id} if vpc_id else {}
    tags_dict = prepare_tags(tags) if tags else {}
    filter_dict = {**vpc_dict, **tags_dict}
    return convert_dict_to_list(filter_dict, "Name", "Values") if filter_dict else []


def get_container_definition_id(task_definition_id: str, container: str) -> str:
    # the reverse logic from https://fburl.com/code/ycdjih3q
    return f"{task_definition_id}#{container}"


def split_container_definition(container_definition: str) -> Tuple[str, str]:
    """
    container_definition = task_definition#container
    task_definition: ECS task definition, e.g. test-definition:1
    container: ECS cluster name, e.g. test-cluster
    example: test-definition:1#test-cluster
    """
    s = container_definition.split("#")
    return (s[0], s[1])
