from typing import List
import datetime
from functools import reduce


class TimeLog:
    def __init__(self, time: datetime, task: str, description: str, duration: int):
        self.time = time
        self.task = task
        self.description = description
        self.duration = duration

    def duration_hours(self):
        return self.duration / 3600