import datetime

from pydantic import BaseModel
from typing import List, Optional


class Trace(BaseModel):
    trace_id: str
    spans: list
    start_time: datetime
    duration: int


class TraceUpdate(BaseModel):
    service_name: str
    last_fetched_start_time: Optional[datetime] = None
    last_fetched_end_time: Optional[datetime] = None
