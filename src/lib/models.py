from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class Status(str, Enum):
    CREATED = 'C'
    MODIFIED = 'M'
    DELETED = 'D'
    COPIED = 'C'


class Diff(BaseModel):
    diff: str
    path: str
    status: Status


class DiffData(BaseModel):
    user: str
    date: datetime
    diffs: List[Diff]
