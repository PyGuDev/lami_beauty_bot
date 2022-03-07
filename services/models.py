from datetime import date, time, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int]
    tg_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]


class Record(BaseModel):
    id: Optional[int]
    user_id: int
    record_date: Optional[date]
    record_time: Optional[time]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class RecordWithUser(BaseModel):
    id: Optional[int]
    user_id: int
    username: Optional[str]
    phone: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
    record_date: Optional[date]
    record_time: Optional[time]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class Events(str, Enum):
    ADD_DATE = 'add_date'
    ADD_TIME = 'add_time'
    ADD_PHONE = 'add_phone'


class RecordEvent(BaseModel):
    id: Optional[int]
    record_id: int
    event: str
