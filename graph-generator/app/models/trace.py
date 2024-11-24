from pydantic import BaseModel
from typing import List


class Trace(BaseModel):
    trace_id: str
    service_name: str
    spans: List[dict]
