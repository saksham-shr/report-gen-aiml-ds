"""
Speaker data model
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Speaker:
    name: str
    activity_id: int
    title_position: Optional[str] = None
    organization: Optional[str] = None
    contact_info: Optional[str] = None
    presentation_title: Optional[str] = None
    profile_image_path: Optional[str] = None
    profile_text: Optional[str] = None
    id: Optional[int] = None

    @property
    def display_name(self) -> str:
        """Get formatted speaker display name"""
        return self.name

    @property
    def full_designation(self) -> str:
        """Get full designation with organization"""
        parts = []
        if self.title_position:
            parts.append(self.title_position)
        if self.organization:
            parts.append(self.organization)
        return ", ".join(parts)

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations"""
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'name': self.name,
            'title_position': self.title_position,
            'organization': self.organization,
            'contact_info': self.contact_info,
            'presentation_title': self.presentation_title,
            'profile_image_path': self.profile_image_path,
            'profile_text': self.profile_text
        }