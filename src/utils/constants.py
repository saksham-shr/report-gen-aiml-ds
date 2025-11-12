"""
Constants for the Activity Report Generator
"""

# Activity types for dropdown
ACTIVITY_TYPES = [
    "Seminar",
    "Workshop",
    "Conference",
    "Technical Talk",
    "Guest Talk",
    "Industry Visit",
    "Sports",
    "Cultural Competition",
    "Technical fest/ Academic fests",
    "CAADS",
    "Research Clubs / or any other Clubs",
    "Newsletter",
    "Alumni",
    "Faculty Development Program",
    "Quality Improvement Program",
    "Refresher Course",
    "MoU",
    "Outreach Activity",
    "International Event"
]

# Sub categories for dropdown
SUB_CATEGORIES = [
    "Competitive Exam",
    "Career Guidance",
    "Skill Development",
    "Communication Skills",
    "Women Event",
    "Emerging Trends and Technology",
    "Life Skills",
    "Soft Skills/ Skill Development",
    "Other"
]

# Participant types
PARTICIPANT_TYPES = [
    ("faculty", "Faculty"),
    ("student", "Student"),
    ("research_scholar", "Research Scholar")
]

# Photo types
PHOTO_TYPES = [
    ("activity", "Activity Photo"),
    ("speaker", "Speaker Photo"),
    ("other", "Other")
]

# University header information
UNIVERSITY_INFO = {
    "name": "Christ(Deemed to be University)",
    "school": "School of Engineering and Technology",
    "department": "Department of AI, ML & Data Science"
}

# File size limits (in bytes)
FILE_SIZE_LIMITS = {
    "activity_photo": 5 * 1024 * 1024,  # 5MB
    "speaker_profile": 5 * 1024 * 1024,  # 5MB
    "signature": 2 * 1024 * 1024  # 2MB
}

# Character limits
TEXT_LIMITS = {
    "speaker_name": 100,
    "title_position": 100,
    "organization": 150,
    "contact_info": 200,
    "presentation_title": 200,
    "venue": 200,
    "preparer_name": 100,
    "preparer_designation": 100,
    "highlights": 2000,
    "key_takeaway": 2000,
    "summary": 3000,
    "follow_up_plan": 2000,
    "speaker_profile": 1000,
    "photo_caption": 100
}

# Limits for dynamic sections
SECTION_LIMITS = {
    "max_speakers": 10,
    "min_speakers": 1,
    "max_participants": 10,
    "min_participants": 1,
    "max_preparers": 5,
    "min_preparers": 1,
    "max_photos": 10,
    "min_photos": 2
}

# Sidebar navigation items
SIDEBAR_ITEMS = [
    ("📋", "General Information"),
    ("👤", "Speaker Details"),
    ("👥", "Participants"),
    ("📝", "Synopsis"),
    ("✍️", "Report Prepared By"),
    ("🔊", "Speaker Profile"),
    ("📷", "Activity Photos"),
    ("📄", "Generate PDF")
]

# Form section order
FORM_SECTIONS = [
    "general_info",
    "speaker_details",
    "participants",
    "synopsis",
    "report_prepared_by",
    "speaker_profile",
    "activity_photos",
    "generate_pdf"
]

# Validation messages
VALIDATION_MESSAGES = {
    "required_field": "This field is required",
    "invalid_date": "Please enter a valid date",
    "invalid_time": "Please enter a valid time",
    "end_before_start": "End date/time cannot be before start date/time",
    "invalid_email": "Please enter a valid email address",
    "invalid_phone": "Please enter a valid phone number",
    "file_too_large": "File size exceeds the maximum limit",
    "invalid_file_type": "Please upload a valid file type (JPG, PNG)",
    "min_photos_required": f"Minimum {SECTION_LIMITS['min_photos']} photos required",
    "at_least_one_speaker": "At least one speaker is required",
    "at_least_one_participant": "At least one participant type is required",
    "at_least_one_preparer": "At least one report preparer is required"
}