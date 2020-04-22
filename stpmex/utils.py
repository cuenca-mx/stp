import datetime as dt
from typing import Union

import pytz


DATE_FORMAT = '%Y%m%d'


def today_mexico_city():
    utc_now = dt.datetime.utcnow().replace(tzinfo=pytz.utc)
    return utc_now.astimezone(pytz.timezone('America/Mexico_City')).date()


def strftime(date: dt.date):
    return date.strftime(DATE_FORMAT)


def strptime(date: Union[int, str]):
    return dt.datetime.strptime(str(date), DATE_FORMAT).date()
