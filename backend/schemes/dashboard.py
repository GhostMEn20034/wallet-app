import datetime

from pydantic import BaseModel
from typing import Optional
from schemes.users import PyObjectId


class DashboardFilter(BaseModel):
    account_id: Optional[PyObjectId]
    start_date: Optional[datetime.datetime]
    end_date: Optional[datetime.datetime]
