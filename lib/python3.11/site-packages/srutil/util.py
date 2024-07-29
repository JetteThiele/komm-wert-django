from ._ioutil import IOUtil
from ._sysutil import SysUtil
from ._pythonutil import PythonUtil
from ._kutil import KnowledgeUtil
from ._numberutil import NumberUtil
from ._stringutil import StringUtil
from ._networkutil import NetworkUtil
from ._datetimeutil import DateTimeUtil


class Util(PythonUtil, IOUtil, SysUtil, StringUtil, NumberUtil, DateTimeUtil, NetworkUtil, KnowledgeUtil):
    pass
