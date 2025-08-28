"""Функции для работы с датой и временем."""
import calendar
import datetime

import pytz
from dateutil import parser as dateparser
from dateutil import tz

ISO_BASIC_FORMAT = "%Y-%m-%dT%H:%M:%S%z"  # noqa: WPS323
DEFAULT_TIMEZONE = "Europe/Moscow"


def utcnow() -> datetime.datetime:
    """
    Возвращает текущее время в UTC.

    :return: datetime UTC.
    """
    return datetime.datetime.utcnow()


def timestamp(
    stamp: datetime.datetime,
    timezone: str = DEFAULT_TIMEZONE,
    milli: bool = False,
) -> int:
    """
    Возвращает UNIX timestamp.

    :param stamp: datetime
    :param timezone: timezone from pytz
    :param milli: if True function return timestamp with milliseconds
    :return: UNIX timestamp
    """
    timegm = calendar.timegm(localize(stamp, timezone=timezone).timetuple())
    if milli:
        timegm *= 1000
    return timegm


def localize(
    stamp: datetime.datetime | datetime.date | None = None,
    timezone: str = DEFAULT_TIMEZONE,
) -> datetime.datetime:
    """
    Перевод времени в выбранную таймзону.

    :param stamp: datetime
    :param timezone: timezone from pytz
    :return: datetime в выбранной таймзоне.
    """
    if stamp is None:
        stamp = utcnow()
    elif not isinstance(stamp, datetime.datetime):
        stamp = datetime.datetime(stamp.year, stamp.month, stamp.day)

    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=pytz.utc)

    return stamp.astimezone(pytz.timezone(timezone))


def timestring(
    stamp: datetime.datetime | datetime.date | None = None,
    timezone: str = DEFAULT_TIMEZONE,
    time_format: str = ISO_BASIC_FORMAT,
):
    """
    Переданную дату конвертнуть в таймзону и отдать в виде строки.

    :param stamp: datetime (если naive, то считается, что это UTC!)
    :param timezone: timezone
    :param time_format: format for timestamp
    :return: string with time
    """
    return localize(stamp=stamp, timezone=timezone).strftime(time_format)


def parse_timestring(
    time_string: str,
    timezone: str = DEFAULT_TIMEZONE,
) -> datetime.datetime:
    """
    Сконвертнуть строку в datetime naive.

    :param time_string: in ISO-8601 format
    :param timezone: if time_string contains no timezone, this argument is used
    :return: naive time in UTC
    """
    time = dateparser.parse(time_string)
    if time.tzinfo is None:
        time = pytz.timezone(timezone).localize(time)
    return time.astimezone(pytz.utc).replace(tzinfo=None)


def parse_timestring_aware(
    time_string: str,
    timezone: str = DEFAULT_TIMEZONE,
) -> datetime.datetime:
    """
    Сконвертнуть строку в datetime aware.

    :param time_string: in ISO-8601 format
    :param timezone: if timestring contains no timezone, this argument is used
    :return: aware time in UTC
    """
    time = dateparser.parse(time_string)
    if time.tzinfo is None:
        time = pytz.timezone(timezone).localize(time)
    return time.astimezone(pytz.utc)


def timestring_to_iso(time_string: str):
    """
    Парсинг timestring в json-совместимый ISO-8601 формат.

    :param time_string: строка времени.
    :return: timestring в json-совместимом ISO-8601 формате
    """
    time = dateparser.parse(time_string)
    if time.tzinfo is None:
        time = time.replace(tzinfo=pytz.UTC)
    return time.isoformat()


def naive_utc_to_naive_tz(
    stamp: datetime.datetime | datetime.date | None = None,
    timezone: str = DEFAULT_TIMEZONE,
):
    """
    Конвертнуть время в UTC во время в таймзоне naive.

    :param stamp: datetime
    :param timezone: str
    :return: datetime naive в нужной таймзоне.
    """
    return localize(stamp, timezone).replace(tzinfo=None)


def naive_tz_to_aware_utc(
    stamp: datetime.datetime,
    timezone: str = DEFAULT_TIMEZONE,
) -> datetime.datetime:
    """
    Конвертнуть время из переданной таймзоны в UTC aware.

    :param stamp: datetime.datetime tz naive object in utc
    :param timezone: str
    :return: datetime.datetime aware
    """
    tz_obj = pytz.timezone(timezone)
    return tz_obj.localize(stamp).astimezone(pytz.utc)


def naive_utc_to_aware_utc(stamp: datetime.datetime) -> datetime.datetime:
    """
    Конвертнуть naive UTC в aware UTC.

    :param stamp: datetime.datetime tz naive object in utc
    :return: datetime.datetime tz aware object in utc
    """
    return stamp.replace(tzinfo=pytz.utc)


def aware_to_naive_utc(stamp: datetime.datetime) -> datetime.datetime:
    """
    Конвертнуть aware UTC в naive UTC.

    :param stamp: datetime.datetime tz naive object in utc
    :return: datetime.datetime tz aware object in utc
    """
    return stamp.astimezone(pytz.utc).replace(tzinfo=None)


def day_start(
    stamp: datetime.datetime,
    utc_offset: str | None = None,
) -> datetime.datetime:
    """
    Возвращает начало сегодня.

    :param stamp: datetime
    :param utc_offset: Смещение относительно UTC
    :return: naive time
    """
    if utc_offset:
        tz_offset = tz.gettz(f"UTC{utc_offset}")
        stamp = stamp.astimezone(tz=tz_offset)
    return stamp.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)


def day_start_with_tz(
    stamp: datetime.datetime,
    utc_offset: str | None = None,
) -> datetime.datetime:
    """
    Возвращает начало сегодня с таймзоной.

    :param stamp: datetime
    :param utc_offset: string
    :return: naive time
    """
    if utc_offset:
        tz_offset = tz.gettz(f"UTC{utc_offset}")
        stamp = stamp.astimezone(tz=tz_offset)
    return stamp.replace(hour=0, minute=0, second=0, microsecond=0)


def day_end(stamp: datetime.datetime) -> datetime.datetime:
    """
    Возвращает конец текущего дня.

    :param stamp: date
    :return: datetime in utc
    """
    return datetime.datetime.combine(stamp, datetime.datetime.max.time())


def today_start(
    stamp: datetime.datetime | datetime.date | None = None,
    timezone: str = DEFAULT_TIMEZONE,
) -> datetime.datetime:
    """
    Вернуть начало сегодняшнего дня (00:00).

    :param stamp: datetime
    :param timezone: timezone from pytz
    :return: Начало дня (00:00).
    """
    return day_start(localize(stamp, timezone=timezone))


def today_start_with_tz(
    stamp: datetime.datetime | datetime.date | None = None,
    timezone: str = DEFAULT_TIMEZONE,
) -> datetime.datetime:
    """
    Вернуть начало сегодняшнего дня в таймзоне (00:00).

    :param stamp: datetime
    :param timezone: timezone from pytz
    :return: Начало дня (00:00).
    """
    return day_start_with_tz(localize(stamp, timezone=timezone))


def tomorrow_start(
    stamp: datetime.datetime | datetime.date | None = None,
    timezone: str = DEFAULT_TIMEZONE,
) -> datetime.datetime:
    """
    Вернуть начало сегодняшнего дня (00:00).

    :param stamp: datetime
    :param timezone: timezone from pytz
    :return: Начало дня (00:00).
    """
    return today_start(stamp, timezone=timezone) + datetime.timedelta(days=1)


def is_aware(stamp: datetime.datetime) -> bool:
    """
    Проверить, что время aware формата.

    :param stamp: datetime
    :return: bool
    """
    return stamp.tzinfo is not None and stamp.tzinfo.utcoffset(stamp) is not None


def is_naive(stamp: datetime.datetime) -> bool:
    """
    Проверить, что время naive формата.

    :param stamp: datetime
    :return: bool
    """
    return not is_aware(stamp)


def utcnow_with_tz() -> datetime.datetime:
    """
    Возвращает текущее время в UTC с таймзоной.

    :return: datetime UTC with tz
    """
    return naive_utc_to_aware_utc(utcnow())


def unix_utc_to_datetime_with_tz(timestamp_unix: int) -> datetime.datetime:
    """
    Вернуть datetime в UTC с таймзоной из timestamp.

    :param timestamp_unix: UNIX timestamp
    :return: datetime in UTC with tz
    """
    return naive_utc_to_aware_utc(datetime.datetime.utcfromtimestamp(timestamp_unix))


def to_aware(stamp: datetime.datetime) -> datetime.datetime:
    """
    Конвертнуть в aware.

    :param stamp: datetime
    :return: datetime aware
    """
    return stamp if is_aware(stamp) else naive_utc_to_aware_utc(stamp)
