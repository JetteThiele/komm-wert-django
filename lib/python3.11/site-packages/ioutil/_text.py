from __future__ import annotations

import os
from typing import AnyStr

from ._file import _File


class Text(_File):

    def write(self, data: AnyStr, path: AnyStr | os.PathLike[AnyStr], mode: str = None) -> bool:
        with self._get_stream(path, mode) as textfile:
            textfile.write(data)
        return os.path.exists(path)

    def read(self, path: AnyStr | os.PathLike[AnyStr], mode: str = None) -> AnyStr:
        """
        :param path: path to target file
        :param mode: reading mode
        :return: string or bytes
        """
        with self._get_stream(path, mode) as textfile:
            return textfile.read()
