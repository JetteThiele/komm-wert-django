from __future__ import annotations
import os
import csv
from srutil import util
from typing import AnyStr, Dict, List

from ._file import _File


class Csv(_File):

    def write(self, data: List[List | Dict], path: AnyStr | os.PathLike[AnyStr], header: list = None,
              mode: str = None) -> bool:
        _temp = data.__getitem__(0)
        if not header:
            header = data.pop(0) if util.isobjtype(_temp, list) else list(_temp.keys())
        with self._get_stream(path, mode) as csvfile:
            if isinstance(_temp, list):
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(header)
                csvwriter.writerows(data)
            elif isinstance(_temp, dict):
                csvwriter = csv.DictWriter(csvfile, fieldnames=header)
                csvwriter.writeheader()
                csvwriter.writerows(data)
        return os.path.exists(path)

    def read(self, path: AnyStr | os.PathLike[AnyStr], mode: str = None, _rfv: bool = False) -> List[List] | str:
        """
        :param path: path to target file
        :param mode: reading mode
        :param _rfv: True will return formatted string
        :return: list of values or formatted string
        """
        to_return = list()
        with self._get_stream(path, mode) as csvfile:
            for line in csv.reader(csvfile):
                to_return.append(line)
        return util.tabulate(to_return, table_fmt="plain") if _rfv else to_return
