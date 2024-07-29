from __future__ import annotations
import os
import pyarrow as pa
from srutil import util
from pathlib import Path
from ioutil import parquet
from typing import AnyStr, Literal

_OPT = Literal['folders', 'files', 'all']


class LocalUtil:
    @staticmethod
    def _extractalpha(value: str) -> str:
        to_return = ''
        for char in value:
            if char.isalpha():
                to_return += char
        return to_return

    @staticmethod
    def _checkandmkdir(path: AnyStr | os.PathLike[AnyStr]) -> None:
        if not os.path.exists(path):
            util.mkdir(path)

    @staticmethod
    def _getpath(_root: AnyStr | os.PathLike[AnyStr], option: str = None) -> list[str]:
        path = os.path.join(util.home(), '.local')
        LocalUtil._checkandmkdir(path=path)
        to_return = []
        _options = ['folders'] if option == 'folders' else ['files'] if option == 'files' else ['folders', 'files']
        for _option in _options:
            to_return.append(
                os.path.join(path, util.stringbuilder(LocalUtil._extractalpha(str(_root)), '_', _option, '.local')))
        return to_return

    @staticmethod
    def _get(_root: AnyStr | os.PathLike[AnyStr],
             option: _OPT = 'all') -> tuple[list, list]:
        files_list = list()
        folders_list = list()
        os.chdir("/")
        for root, dirs, files in os.walk(top=_root):
            root = str(Path(root).resolve())
            if option in ['all', 'folders']:
                folders_list.append(root)
            if option in ['all', 'files']:
                for file in files:
                    files_list.append(str(Path(root).joinpath(file).resolve()))
        return folders_list, files_list

    @staticmethod
    def _analyse(_root: AnyStr | os.PathLike[AnyStr],
                 option: _OPT = 'all') -> None:
        folders, files = LocalUtil._get(_root, option)
        _store_obj = []
        _d = dict()
        if option in ['all', 'folders']:
            _d.setdefault('folders', folders)
            _store_obj.append(_d)
        if option in ['all', 'files']:
            _d = dict() if len(_d) > 0 else _d
            _d.setdefault('files', files)
            _store_obj.append(_d)
        for d in _store_obj:
            _option = 'folders' if 'folders' in d else 'files' if 'files' else None
            path = LocalUtil._getpath(_root, _option).pop()
            parquet.write(data=d, path=path)

    @staticmethod
    def getdata(_root: AnyStr | os.PathLike[AnyStr],
                option: _OPT = 'all', refresh: bool = False) -> list:
        if refresh:
            LocalUtil._analyse(_root=_root, option=option)
        data = list()
        for path in LocalUtil._getpath(_root, option):
            if not os.path.exists(path):
                LocalUtil._analyse(_root=_root, option=option)
            _data_dict = pa.Table.from_pandas(df=parquet.read(path=path)).to_pydict()
            for opt in ['folders', 'files']:
                if opt in _data_dict:
                    data.extend(_data_dict.get(opt))
        return data
