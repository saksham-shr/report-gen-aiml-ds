"""
Participant data model
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Participant:
    participant_type: str  # 'faculty', 'student', 'research_scholar'
    count: int
    activity_id: int
    id: Optional[int] = None

    @property
    def display_type(self) -> str:
        """Get formatted participant type display"""
        type_mapping = {
            'faculty': 'Faculty',
            'student': 'Students',
            'research_scholar': 'Research Scholars'
        }
        return type_mapping.get(self.participant_type, self.participant_type.title())

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'participant_type': self.participant_type,
            'count': self.count
        }