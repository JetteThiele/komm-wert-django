from __future__ import annotations

import json
import os
from typing import AnyStr

from ._file import _File


class Json(_File):

    def write(self, data: str | dict, path: AnyStr | os.PathLike[AnyStr], mode: str = None) -> bool:
        _json_obj = json.dumps(data)
        with self._get_stream(path, mode) as jsonfile:
            json.dump(_json_obj, jsonfile)
        return os.path.exists(path)

    def read(self, path: AnyStr | os.PathLike[AnyStr], mode: str = None) -> dict:
        """
        :param path: path to target json file
        :param mode: reading mode
        :return: dict values
        """
        with self._get_stream(path, mode) as jsonfile:
            return json.load(jsonfile)
