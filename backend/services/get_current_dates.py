import datetime
import calendar
from dateutil.relativedelta import relativedelta


def get_current_dates():
    now = datetime.datetime.utcnow()  # current time
    # Use datetime.combine to combine the date with a time of 23:59:59
    end_of_current_day = datetime.datetime.combine(now, datetime.time(23, 59, 59))
    thirty_days_ago = end_of_current_day - relativedelta(days=30)  # datetime 30 days ago
    sixty_days_ago = thirty_days_ago - relativedelta(days=60)  # datetime 60 days ago

    return {"end_of_current_day": end_of_current_day,
            "thirty_days_ago": thirty_days_ago,
            "sixty_days_ago": sixty_days_ago,
            }
