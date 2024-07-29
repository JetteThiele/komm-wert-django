"""to read and write files"""
from __future__ import annotations
import os
from srutil import util
from typing import Literal, Any, AnyStr

from ioutil._file import _File
from ioutil._csv import Csv
from ioutil._text import Text
from ioutil._toml import TOML
from ioutil._json import Json
from ioutil._parquet import Parquet

_FS = Literal["csv", "json", "parquet", "toml", "text"]


class File:
    @staticmethod
    def __getinstance(path: AnyStr | os.PathLike = None, _format: _FS = None) -> _File:
        if path and not _format:
            ext = list(os.path.splitext(path)).pop()
            _format = {".csv": "csv", ".json": "json", ".parquet": ".parquet", ".toml": "toml", ".txt": "text"}.get(ext)
        if _format:
            _instance = {"csv": Csv, "json": Json, "parquet": Parquet, "toml": TOML, "text": Text}.get(_format)
            return _instance()
        else:
            raise ValueError("Invalid file type")

    @staticmethod
    def __remove_unwanted_params(f: _File, params: dict) -> dict:
        method_list = {'read': f.read, 'write': f.write}
        params_of_method = util.paramsofmethod(method_list.get(util.whocalledme())).keys()
        new_params = dict()
        for key, value in params.items():
            if key in params_of_method:
                new_params.setdefault(key, value)
        return new_params

    @staticmethod
    def read(path: AnyStr | os.PathLike, _format: _FS = None, **kwargs) -> Any:
        f = File.__getinstance(path=path, _format=_format)
        kwargs = File.__remove_unwanted_params(f, kwargs)
        return f.read(path=path, **kwargs)

    @staticmethod
    def write(data, path: AnyStr | os.PathLike, _format: _FS = None, **kwargs) -> bool:
        f = File.__getinstance(path=path, _format=_format)
        kwargs = File.__remove_unwanted_params(f, kwargs)
        return f.write(data=data, path=path, **kwargs)


csv = Csv()
json = Json()
parquet = Parquet()
text = Text()
toml = TOML()

__author__ = 'srg'
__version__ = '1.0.3'

__all__ = [
    'File',
    'csv',
    'json',
    'parquet',
    'toml',
    'text'
]
