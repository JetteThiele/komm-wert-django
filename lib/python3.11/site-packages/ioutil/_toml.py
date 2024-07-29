from __future__ import annotations

import os
import toml
from typing import AnyStr, Any, Mapping

from ._file import _File


class TOML(_File):

    def write(self, data: Mapping[str, Any], path: AnyStr | os.PathLike[AnyStr], mode: str = None) -> bool:
        with self._get_stream(path, mode) as toml_file:
            toml.dump(data, toml_file)
        return os.path.exists(path)

    def read(self, path: AnyStr | os.PathLike[AnyStr], mode: str = None) -> dict[str, Any]:
        """
        :param path: path to target json file
        :param mode: reading mode
        :return: dict values
        """
        with self._get_stream(path, mode) as toml_file:
            return toml.load(toml_file)
