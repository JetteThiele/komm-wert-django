import os
import sys
import getpass
import inspect
import subprocess
from pathlib import Path
from typing import Literal, Any, cast
from pkg_resources import get_distribution, DistributionNotFound

from ._metautil import Meta


class PythonUtil:
    _current_working_dir = os.getcwd()

    @staticmethod
    def isobjtype(instance: object, cls: type) -> bool:
        """
        True if `obj` is instanceof `cls`.
        """
        return type(instance) is cls or isinstance(instance, cls)

    @staticmethod
    def getinstanceof(obj: Any, target: object, default=None) -> object:
        """
        Cast `obj` to `target` type.
        """
        to_return = default
        if not isinstance(target, type):
            target = type(target)
        try:
            to_return = cast(target, obj)  # target(obj)
        except TypeError as ignored:
            return to_return

    @staticmethod
    def whoami() -> str:
        """
        :return: name of current function/method.
        """
        return inspect.currentframe().f_back.f_code.co_name

    @staticmethod
    def whocalledme() -> str:
        """
        :return: name of caller of current function/method.
        """
        to_return = None
        try:
            to_return = inspect.currentframe().f_back.f_back.f_code.co_name
        except AttributeError as e:
            pass
        return to_return

    @staticmethod
    def paramsofmethod(_callable: callable):
        """
        :return: params of given callable.
        """
        return inspect.signature(_callable).parameters

    @staticmethod
    def removeunwantedparams(_callable: callable, **kwargs) -> dict:
        params_of_method = PythonUtil.paramsofmethod(_callable).keys()
        new_params = dict()
        for key, value in kwargs.items():
            if key in params_of_method:
                new_params.setdefault(key, value)
        return new_params

    @staticmethod
    def getpackageversion(dist: str) -> str:
        try:
            return get_distribution(dist).version
        except DistributionNotFound as e:
            return e.__str__()

    @staticmethod
    def metaclass(_for: Literal['interface', 'singleton', 'attribute_holder']):
        """
        Example Usage:
         class Inter(metaclass=metaclass('singleton'):
             pass
        """
        _meta_class = {'interface': Meta.interface, 'singleton': Meta.singleton,
                       'attribute_holder': Meta.attribute_holder}
        return _meta_class.get(_for)

    @staticmethod
    def uploadpackagetopypi(path: str = _current_working_dir, to: Literal["pypi", "testpypi"] = "testpypi",
                            show_process: bool = False) -> Any:
        """
        upload python package to pypi.

        :param path: directory where pyproject.toml/setup.py is located
        :param to: upload to
        :param show_process: True will show the output
        """
        py_syn = {**dict.fromkeys(["darwin", "linux"], "python3"), **dict.fromkeys(["win32", "cygwin"], "py")}
        py = py_syn.get(sys.platform)
        sp = {"call": subprocess.call, "check_output": subprocess.check_output}
        process = sp.get("call") if show_process else sp.get("check_output")
        try:
            # Make sure you have the latest version of pip installed
            process("{} -m pip install --upgrade pip".format(py), stderr=subprocess.STDOUT)
            # Make sure you have the latest version of PyPA’s build installed
            process("{} -m pip install --upgrade build".format(py), stderr=subprocess.STDOUT)
            # once completed should generate two files in the dist directory
            os.chdir(path)
            PythonUtil.current_working_dir = os.getcwd()
            process("{} -m build".format(py), stderr=subprocess.STDOUT)
            # Make sure you have the latest version of twine build installed
            process("{} -m pip install --upgrade twine".format(py), stderr=subprocess.STDOUT)
            # uploading the distribution archives
            upload_option = {"pypi": "", "testpypi": "--repository testpypi"}
            signin_opt = ""
            if to == "testpypi" or os.path.exists(os.path.join(Path.home(), ".pypirc")):
                username = input("Enter your username: ")
                password = getpass.getpass(prompt="Enter your password: ")
                signin_opt = "--username {} --password {}".format(username, password)
            upload_out = process(
                "{} -m twine upload {} {} dist/* --disable-progress-bar".format(py, signin_opt, upload_option.get(to)),
                stderr=subprocess.STDOUT)
            if not show_process:
                return upload_out
        except subprocess.CalledProcessError as e:
            return e.output.decode("ascii") if isinstance(e.output, bytes) else e.output
