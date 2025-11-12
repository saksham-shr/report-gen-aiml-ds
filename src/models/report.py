"""
Report data model for combining all activity-related data
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ReportPreparer:
    name: str
    activity_id: int
    designation: Optional[str] = None
    signature_image_path: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'name': self.name,
            'designation': self.designation,
            'signature_image_path': self.signature_image_path
        }

@dataclass
class ActivityPhoto:
    photo_path: str
    activity_id: int
    photo_type: str = 'activity'
    caption: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'photo_path': self.photo_path,
            'photo_type': self.photo_type,
            'caption': self.caption
        }

@dataclass
class ActivityReport:
    activity: dict
    speakers: List[dict]
    participants: List[dict]
    report_preparers: List[dict]
    photos: List[dict]

    def validate_minimum_requirements(self) -> List[str]:
        """Validate minimum requirements for report generation"""
        errors = []

        if not self.activity.get('activity_type'):
            errors.append("Activity type is required")

        if not self.activity.get('start_date'):
            errors.append("Start date is required")

        if len(self.speakers) == 0:
            errors.append("At least one speaker is required")

        if len(self.participants) == 0:
            errors.append("At least one participant type is required")

        if len(self.photos) < 2:
            errors.append("At least 2 activity photos are required for PDF generation")

        if len(self.report_preparers) == 0:
            errors.append("At least one report preparer is required")

        return errors