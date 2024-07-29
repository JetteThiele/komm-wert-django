from __future__ import annotations

import re
import sys
import uuid
import socket
import subprocess
import os.path
from pathlib import Path
from typing import AnyStr, Any, Sequence
from send2trash import send2trash


class SysUtil:
    @staticmethod
    def home() -> str:
        home_dir = str(Path().home())
        return os.path.abspath(path=home_dir)

    @staticmethod
    def hostname() -> str:
        return socket.gethostname()

    @staticmethod
    def ipaddress() -> str:
        return socket.gethostbyname(SysUtil.hostname())

    @staticmethod
    def macaddress() -> str:
        return ':'.join(re.findall('..', '%012x' % uuid.getnode()))

    @staticmethod
    def myos() -> str | None:
        os_list = {
            "darwin": "macOS",
            **dict.fromkeys(["win32", "cygwin"], "Windows"),
            "linux": "Linux"
        }
        for key, value in os_list.items():
            if key in sys.platform:
                return value
        return None

    @staticmethod
    def getfilesize(path: AnyStr | os.PathLike[AnyStr]) -> int:
        """
        returns size in bytes.
        """
        return os.path.getsize(path)

    @staticmethod
    def delete(path: AnyStr | os.PathLike[AnyStr], permanently: bool = False) -> None:
        """
        :param path: file/folder path
        :param permanently: False will move files/folders to trash, True will delete them permanently
        :return: None
        """
        if not permanently:
            send2trash(path)
        else:
            os.remove(path)

    @staticmethod
    def executesyscmd(cmd: AnyStr | os.PathLike[AnyStr] | Sequence[AnyStr | os.PathLike[AnyStr]],
                      return_output: bool = False) -> Any | None:
        sp = {"call": subprocess.call, "check_output": subprocess.check_output}
        process = sp.get("call") if not return_output else sp.get("check_output")
        try:
            to_return = process(cmd, stderr=subprocess.STDOUT)
            if return_output:
                return to_return
        except subprocess.CalledProcessError as e:
            return e.output.decode("ascii") if isinstance(e.output, bytes) else e.output

    @staticmethod
    def mkdir(path: str) -> bool:
        path_parts = Path(path).parts
        fd = None
        for part in path_parts:
            fd = part if not fd else os.path.join(fd, part)
            if not os.path.exists(fd):
                os.mkdir(path=fd)
        return os.path.exists(path)
