"""
Activity data model
"""

from dataclasses import dataclass
from datetime import date, time
from typing import Optional

@dataclass
class Activity:
    activity_type: str
    start_date: date
    sub_category: Optional[str] = None
    sub_category_other: Optional[str] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    venue: Optional[str] = None
    collaboration_sponsor: Optional[str] = None
    highlights: Optional[str] = None
    key_takeaway: Optional[str] = None
    summary: Optional[str] = None
    follow_up_plan: Optional[str] = None
    id: Optional[int] = None

    @property
    def duration_days(self) -> int:
        """Calculate duration in days"""
        if self.end_date and self.start_date:
            return (self.end_date - self.start_date).days + 1
        return 1

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'sub_category': self.sub_category,
            'sub_category_other': self.sub_category_other,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'venue': self.venue,
            'collaboration_sponsor': self.collaboration_sponsor,
            'highlights': self.highlights,
            'key_takeaway': self.key_takeaway,
            'summary': self.summary,
            'follow_up_plan': self.follow_up_plan
        }