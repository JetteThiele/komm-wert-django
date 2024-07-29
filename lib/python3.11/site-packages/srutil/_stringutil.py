import re

from ._pythonutil import PythonUtil


class StringBuilder(PythonUtil.metaclass('attribute_holder')):
    def __init__(self):
        self.value = None

    def append(self, string: str, separator: str = "") -> "StringBuilder":
        itr = []
        if self.value:
            itr.append(self.value)
        itr.append(string)
        if string:
            self.value = separator.join(itr)
        return self

    def tostring(self) -> str:
        return str(self.value) if self.value else ''


class StringUtil:
    @staticmethod
    def replacesubstringswithastring(*pattern, string: str, repl: str = "") -> str:
        """
        replace substrings `*pattern` with `string`
        Example: replacesubstringswithastring('a', 'b', string='abcd', repl='x') -> 'xxcd'
        """
        new_string = re.sub(StringUtil.stringbuilder(*pattern, separator='|'), repl, string)
        return new_string

    @staticmethod
    def stringbuilder(*args: str, separator: str = "") -> str:
        """
        append tuple of strings using separator
        example: stringbuilder("a", "b", "c", separator=".") -> 'a.b.c'
        """
        sb = StringBuilder()
        for arg in args:
            sb.append(arg, separator=separator)
        return sb.tostring()
