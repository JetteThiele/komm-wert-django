from __future__ import annotations

import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from typing import AnyStr

from ._file import _File


class Parquet(_File):

    def write(self, data: dict, path: AnyStr | os.PathLike[AnyStr]) -> bool:
        dataframe = pd.DataFrame.from_dict(data)
        table = pa.Table.from_pandas(df=dataframe)
        pq.write_table(table, path)
        return os.path.exists(path)

    def read(self, path: AnyStr | os.PathLike[AnyStr]) -> pd.DataFrame | pd.Series:
        """
        :param path: path to target parquet file
        :return: pandas dataframe
        """
        table = pq.read_table(path)
        return table.to_pandas()
