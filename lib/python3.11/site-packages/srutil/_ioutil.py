from __future__ import annotations
import getpass as gp
import tabulate as tb
import pyperclip as pc
from typing import TextIO, Mapping, Iterable, Sequence


class IOUtil:
    @staticmethod
    def to_clipboard(text: str) -> bool:
        pc.copy(text)
        return text == IOUtil.from_clipboard()

    @staticmethod
    def from_clipboard():
        return pc.paste()

    @staticmethod
    def getpass(prompt='Password: ', stream: TextIO | None = None):
        """Prompt for a password, with echo turned off."""
        return gp.getpass(prompt=prompt, stream=stream)

    @staticmethod
    def tabulate(tabular_data: Mapping[str, Iterable] | Iterable[Iterable],
                 headers: str | dict[str, str] | Sequence[str] = (), table_fmt: str | tb.TableFormat = "simple",
                 float_fmt: str | Iterable[str] = "g", num_align: str | None = "", str_align: str | None = "default",
                 missing_val: str | Iterable[str] = "", show_index: str | bool | Iterable = "default",
                 disable_numparse: bool | Iterable[int] = False, col_align: Iterable[str | None] | None = None) -> str:
        return tb.tabulate(tabular_data=tabular_data, headers=headers, tablefmt=table_fmt, floatfmt=float_fmt,
                           numalign=num_align, stralign=str_align, missingval=missing_val, showindex=show_index,
                           disable_numparse=disable_numparse, colalign=col_align)
