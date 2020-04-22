import datetime as dt

from stpmex.utils import strftime, strptime


def test_strftime():
    assert strftime(dt.date(2020, 4, 20)) == '20200420'


def test_strptime():
    assert strptime('20200420') == dt.date(2020, 4, 20)
