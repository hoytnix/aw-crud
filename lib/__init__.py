import datetime
import pytz


def current_year():
    return datetime.datetime.now(pytz.utc).year
