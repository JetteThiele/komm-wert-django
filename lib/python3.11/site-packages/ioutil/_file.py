from __future__ import annotations

import abc
import os
from srutil import util
from typing import AnyStr

meta_interface = util.metaclass('interface')


class IOInterface(metaclass=meta_interface):

    def write(self, data: AnyStr, path: AnyStr | os.PathLike[AnyStr], **kwargs) -> bool:
        pass

    def read(self, path: AnyStr | os.PathLike[AnyStr], **kwargs):
        pass


class _File:
    @staticmethod
    def _get_stream(file: AnyStr | os.PathLike[AnyStr], mode: str):
        if not mode:
            mode = {'read': 'r', 'write': 'w'}.get(util.whocalledme())
        return open(file, mode)

    @abc.abstractmethod
    def write(self, **kwargs) -> bool:
        pass

    @abc.abstractmethod
    def read(self, **kwargs):
        pass
