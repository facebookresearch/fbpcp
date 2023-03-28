# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json, DataClassJsonMixin, Undefined


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Insight(DataClassJsonMixin):
    def convert_to_str_with_class_name(self) -> str:
        class_name = {"class_name": self.__class__.__name__}
        insight = self.to_dict()
        insight.update(class_name)
        return json.dumps(insight)
