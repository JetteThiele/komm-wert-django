from __future__ import annotations
import os
import webbrowser
from srutil import util
from pathlib import Path
from typing import AnyStr

from .util import _OPT, LocalUtil as Lu


class Local:
    def __init__(self, root: AnyStr | os.PathLike[AnyStr],
                 option: _OPT = 'all', refresh: bool = False):
        self.result = None
        self.__categorized_key = ["ExactMatches[E]", "Videos[V]", "Executables[X]", "Audios[A]",
                                  "Images[I]", "Documents[D]", "Shortcuts[S]", "Compressed[C]",
                                  "ProgrammingFiles[P]", "Folders[F]", "UnCategorized[U]", "Deleted[B]"]
        self.__supported_ext = [[".mkv", ".mp4", ".webm"], [".exe"], [".mp3", ".wav"], [".png", ".jpg", ".jpeg"],
                                [".txt", ".pdf", ".pptx", ".ppt", ".docx", ".csv", ".xlsx"], [".lnk"],
                                [".zip", ".rar"],
                                [".py", ".java", ".html", ".htm", ".ipynb", ".php", ".rb", ".jl", ".c", ".cpp"]]
        self._set_values(root, option, refresh)
        pass

    def _set_values(self, root: AnyStr | os.PathLike[AnyStr],
                    option: _OPT = 'all', refresh: bool = False) -> 'Local':
        self.root = root
        self.option = option
        self.refresh = refresh
        self.include_folders = option == "all" or option == "folders"
        return self

    @staticmethod
    def _filter(data: list, *keys) -> list:
        filtered_data = list()
        for value in data:
            if len(keys) > 0:
                for key in keys:
                    if key.lower() not in Path(value).parts[-1].lower():
                        break
                    elif key == keys[-1]:
                        filtered_data.append(value)
                        data.remove(value)
        return list(set(filtered_data))

    def _categorize(self, *keys, data: list, include_deleted: bool = False) -> dict:
        supported_formats = dict(zip(self.__categorized_key[1:9], self.__supported_ext))
        categorized_value = list()
        for i in range(len(self.__categorized_key)):
            categorized_value.append(list())
        categorized_result = dict(zip(self.__categorized_key, categorized_value))
        resultant_len = len(data)
        for i in range(resultant_len):
            result = data[0]
            file_ext = os.path.splitext(result)[-1]
            file_name = result.split("/")[-1].replace(file_ext, "") if os.path.isfile(result) else result.split("/")[-1]
            if (result[0] + ":/$Recycle.Bin").lower() in result[:15].lower():
                if include_deleted:
                    categorized_result.get("Deleted[B]").append(result)
                data.remove(result)
                continue
            if len(keys) == 1 and keys[0].lower() == file_name.lower():
                categorized_result.get("ExactMatches[E]").append(result)
            if os.path.isdir(result):
                categorized_result.get("Folders[F]").append(result)
                data.remove(result)
            elif os.path.isfile(result):
                for form in supported_formats:
                    if file_ext in supported_formats.get(form):
                        categorized_result.get(form).append(result)
                        data.remove(result)
                        break
                else:
                    categorized_result.get("UnCategorized[U]").append(result)
                    data.remove(result)
            elif not os.path.exists(result):
                data.remove(result)
        categorized_result.get("UnCategorized[U]").extend(data)
        categorized_result = {key: value for key, value in categorized_result.items() if len(value) > 0}
        return categorized_result

    def _getfile_category(self, file_to_open: str) -> list[str]:
        try:
            file_to_open = file_to_open.replace("-", "")
            to_return = list()
            for category in self.__categorized_key:
                if "[" + file_to_open[0].upper() + "]" in category:
                    to_return.append(category)
                    to_return.append(self.result.get(category)[int(file_to_open[-1]) - 1])
                    return to_return
            else:
                raise ValueError("Given option is invalid ")
        except Exception:
            raise ValueError("Given option is invalid ")

    def prompt(self):
        print(end="\n")
        to_open = input("Enter your option [category-index]: ")
        in_explorer = input("Do you want to open in Explorer [y|n]: ").lower() == 'y'
        self.open(to_open, in_explorer)

    def search(self, *keys, **kwargs) -> 'Local':
        """
        display=True, prints result.
        """
        _kwargs = util.removeunwantedparams(self._set_values, **kwargs)
        if len(_kwargs) > 0:
            self._set_values(**_kwargs)
        _data = Lu.getdata(self.root, self.option, self.refresh)
        self.result = self._categorize(*keys, data=self._filter(_data, *keys))
        if "display" in kwargs:
            self.display()
        if "prompt" in kwargs:
            self.prompt()
        return self

    def display(self) -> None:
        if len(self.result) > 0:
            print("Match Found :")
            for key, values in self.result.items():
                print("\n" + key.title() + "\n")
                for i in range(len(values)):
                    print(str(i + 1) + ".", values[i].title())
        else:
            print("No Match Found")

    def open(self, to_open: str, in_explorer: bool = False) -> None:
        """
        open in File Explorer.

        Example:
            >> local = Local(root="../path")
            >> local.search("file", "name", display=True)
            >> local.open(to_open="F-1")  # to open first result in 'Folder' category.

        :return: None
        """
        if not self.result:
            raise Exception("Nothing to open")
        file_category, file = self._getfile_category(file_to_open=to_open)
        _to_open = file if os.path.isdir(file) and file_category != "Deleted[B]" else os.path.dirname(file)
        if in_explorer:
            webbrowser.open(_to_open)
        else:
            _open_cmd = {"macOS": "open", "Linux": "xdg-open", "Windows": "start"}.get(util.myos())
            try:
                util.executesyscmd([_open_cmd, Path(file)])
            except FileNotFoundError:
                os.startfile(file)
