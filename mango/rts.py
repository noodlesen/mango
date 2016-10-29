# Readable Time Stamp library NOT USED?
from datetime import datetime
from time import sleep
import random


class RTS():

    __FORMAT_STRING = '%y%m%d%H%M%S'

    @staticmethod
    def utc_now():
        return ( int(datetime.utcnow().strftime(RTS.__FORMAT_STRING)) )

    @staticmethod
    def from_datetime(dt):
        return (dt.strftime(RTS.__FORMAT_STRING))

    @staticmethod
    def to_datetime(rt):
        return (str(rt).strptime(RTS.__FORMAT_STRING))


def get_random_datetime(year_from, year_to, month_from=1, month_to=12, day_from=1, day_to=28, hour_from=0, hour_to=23, minute_from=0, minute_to=59, second_from=0, second_to=59):
    year = random.randint(year_from, year_to)
    month = random.randint(month_from, month_to)
    day = random.randint(day_from, day_to)
    hour = random.randint(hour_from, hour_to)
    minute = random.randint(minute_from, minute_to)
    second = random.randint(second_from, second_to)
    return datetime(year, month, day, hour, minute, second)