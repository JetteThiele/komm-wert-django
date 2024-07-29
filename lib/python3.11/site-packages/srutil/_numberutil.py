import math
import random
from typing import Tuple


class NumberUtil:
    @staticmethod
    def bit_size(num: int) -> int:
        try:
            return num.bit_length()
        except AttributeError as e:
            raise TypeError("bit_size(num) only supports integers, not %r" % type(num)) from e

    @staticmethod
    def byte_size(num: int) -> int:
        return 1 if num == 0 else NumberUtil.ceil(num, 8)

    @staticmethod
    def ceil(num: int, div: int) -> int:
        quotient, remainder = divmod(num, div)
        if remainder:
            quotient += 1
        return quotient

    @staticmethod
    def rand_num(start: int, stop: int) -> int:
        num = random.randrange(start, stop)
        return num

    @staticmethod
    def _all_nearest_power_of_n(x: int, n: int) -> Tuple[int, int]:
        lg = math.log(x) // math.log(n)
        a = int(pow(n, lg))
        b = int(pow(n, lg + 1))
        return a, b

    @staticmethod
    def nearest_power_of_n(x: int, n: int) -> int:
        a, b = NumberUtil._all_nearest_power_of_n(x, n)
        if (x - a) < (b - x):
            return a
        return b

    @staticmethod
    def ext_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """Returns a tuple (r, i, j) such that r = gcd(a, b) = ia + jb"""
        ori_a = a
        ori_b = b
        x = 0
        y = 1
        lx = 1
        ly = 0
        while b != 0:
            quot = a // b
            (a, b) = (b, a % b)
            (x, lx) = ((lx - (quot * x)), x)
            (y, ly) = ((ly - (quot * y)), y)
        if lx < 0:
            lx += ori_b
        if ly < 0:
            ly += ori_a
        return a, lx, ly  # Return only positive values

    @staticmethod
    def mod_inv(x: int, n: int) -> int:
        """Returns the inverse of x % n under multiplication, a.k.a x^-1 (mod n)"""
        (div, inv, _) = NumberUtil.ext_gcd(x, n)
        if div != 1:
            raise Exception(x, n, div)
        return inv
