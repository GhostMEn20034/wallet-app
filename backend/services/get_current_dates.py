import datetime
import calendar
from dateutil.relativedelta import relativedelta


def get_current_dates():
    today = datetime.date.today()

    # Get the first day of the current month
    first_day_current = today.replace(day=1)
    # The last day of the current month
    last_day_current = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    # Get the first day of the past month
    first_day_past = first_day_current - relativedelta(months=1)
    last_day_past = first_day_past.replace(day=calendar.monthrange(first_day_past.year, first_day_past.month)[1])

    # Get the datetime with the first day of the current month
    # Use datetime.combine to combine the date with a time of 00:00:00
    first_day_current_datetime = datetime.datetime.combine(first_day_current, datetime.time(0, 0, 0))

    # Get the datetime with the last day of the current month
    # Use datetime.combine to combine the date with a time of 23:59:59
    last_day_current_datetime = datetime.datetime.combine(last_day_current, datetime.time(23, 59, 59))

    # Get the datetime with the first day of the past month
    # Use datetime.combine to combine the date with a time of 00:00:00
    first_day_past_datetime = datetime.datetime.combine(first_day_past, datetime.time(0, 0, 0))

    # Get the datetime with the last day of the past month
    # Use datetime.combine to combine the date with a time of 23:59:59
    last_day_past_datetime = datetime.datetime.combine(last_day_past, datetime.time(23, 59, 59))
    # print("Datetime with the first day of the current month:", first_day_current_datetime)
    # print("Datetime with the last day of the current month:", last_day_current_datetime)
    # print("Datetime with the first day of the past month:", first_day_past_datetime)
    # print("Datetime with the last day of the past month:", last_day_past_datetime)

    return {"first_day_of_current_date": first_day_current_datetime,
            "last_day_of_current_date": last_day_current_datetime,
            "first_day_of_past_date": first_day_past_datetime,
            "last_day_of_past_date": last_day_past_datetime}
