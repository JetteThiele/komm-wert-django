import calendar
import time
from datetime import datetime


class DateTimeUtil:
    @staticmethod
    def epoch() -> str:
        return str(calendar.timegm(datetime.now().timetuple()))

    @staticmethod
    def now() -> datetime:
        return datetime.now()

    @staticmethod
    def current_in_millis() -> float:
        return time.time() * 1000
