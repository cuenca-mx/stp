import datetime as dt

from stpmex.utils import strftime, strptime, today_mexico_city


def test_today_mexico_city(mocker):
    mock_datetime = mocker.patch('stpmex.utils.dt')
    mock_datetime.datetime.utcnow.return_value = dt.datetime(2020, 4, 20, 1)
    assert today_mexico_city() == dt.date(2020, 4, 19)


def test_strftime():
    assert strftime(dt.date(2020, 4, 20)) == '20200420'


def test_strptime():
    assert strptime('20200420') == dt.date(2020, 4, 20)
