"""
Report data model for combining all activity-related data
"""

from dataclasses import dataclass
from typing import List, Optional
from .activity import Activity
from .speaker import Speaker
from .participant import Participant

@dataclass
class ReportPreparer:
    name: str
    activity_id: int
    designation: Optional[str] = None
    signature_image_path: Optional[str] = None
    id: Optional[int] = None

    @property
    def display_name_with_designation(self) -> str:
        """Get formatted name with designation"""
        if self.designation:
            return f"{self.name}, {self.designation}"
        return self.name

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
    photo_type: str = 'activity'  # 'activity', 'speaker', 'other'
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
    activity: Activity
    speakers: List[Speaker]
    participants: List[Participant]
    report_preparers: List[ReportPreparer]
    photos: List[ActivityPhoto]

    @property
    def total_participants(self) -> int:
        """Calculate total number of participants"""
        return sum(p.count for p in self.participants)

    @property
    def participant_types_display(self) -> str:
        """Get formatted participant types display"""
        type_counts = {}
        for participant in self.participants:
            type_counts[participant.display_type] = type_counts.get(participant.display_type, 0) + participant.count

        return ", ".join([f"{count} {ptype}" for ptype, count in type_counts.items()])

    def validate_minimum_requirements(self) -> List[str]:
        """Validate minimum requirements for report generation"""
        errors = []

        if not self.activity.activity_type:
            errors.append("Activity type is required")

        if not self.activity.start_date:
            errors.append("Start date is required")

        if len(self.speakers) == 0:
            errors.append("At least one speaker is required")

        if not all(speaker.name for speaker in self.speakers):
            errors.append("All speakers must have a name")

        if len(self.participants) == 0:
            errors.append("At least one participant type is required")

        if not all(p.count > 0 for p in self.participants):
            errors.append("All participant counts must be greater than 0")

        if len(self.photos) < 2:
            errors.append("At least 2 activity photos are required for PDF generation")

        if len(self.report_preparers) == 0:
            errors.append("At least one report preparer is required")

        if not all(p.name and p.designation for p in self.report_preparers):
            errors.append("All report preparers must have name and designation")

        return errors

    def to_dict(self) -> dict:
        """Convert complete report to dictionary"""
        return {
            'activity': self.activity.to_dict(),
            'speakers': [s.to_dict() for s in self.speakers],
            'participants': [p.to_dict() for p in self.participants],
            'report_preparers': [rp.to_dict() for rp in self.report_preparers],
            'photos': [p.to_dict() for p in self.photos]
        }