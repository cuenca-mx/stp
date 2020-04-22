import datetime as dt
from typing import Union

DATE_FORMAT = '%Y%m%d'


def strftime(date: dt.date):
    return date.strftime(DATE_FORMAT)


def strptime(date: Union[int, str]):
    return dt.datetime.strptime(str(date), DATE_FORMAT).date()
