# -*- coding: utf-8 -*-
"""Time and date utility functions."""

# standard library imports
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

# third-party imports

# application imports

DATE_FORMAT = '%Y-%m-%d'
LOCAL_TZ = pytz.timezone("America/Toronto")


def string_to_date(date_str):
    """Convert a string date to a datetime.

    Args:
        date_str: A date in the above DATE_FORMAT format

    Returns:
        A Date object

    """
    date_time = datetime.strptime(date_str, DATE_FORMAT)
    # return date(date_time.year, date_time.month, date_time.day)
    return date_time.date()


def add_years(start_date, years):
    """Return a date in the future.

    Args:
        start_date: The date to change
        years: number of years to add

    Returns:
        The adjusted date

    """
    if start_date is None:
        return None

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, DATE_FORMAT)

    return start_date + relativedelta(years=years)
