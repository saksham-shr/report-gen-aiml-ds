"""
Form validation service
"""

import re
from datetime import datetime, date, time
from typing import Dict, Any, List, Optional, Tuple

class ValidationService:
    """Service for validating form inputs and data"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format (basic validation)"""
        # Remove common separators
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)

        # Check if it's a valid phone number (10-15 digits)
        return clean_phone.isdigit() and len(clean_phone) >= 10 and len(clean_phone) <= 15

    @staticmethod
    def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
        """Validate date string"""
        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_time(time_str: str, format_str: str = "%H:%M") -> bool:
        """Validate time string"""
        try:
            datetime.strptime(time_str, format_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_date_range(start_date: str, end_date: str, date_format: str = "%Y-%m-%d") -> Tuple[bool, str]:
        """
        Validate date range (end date must be >= start date)

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            start = datetime.strptime(start_date, date_format).date()
            end = datetime.strptime(end_date, date_format).date()

            if end < start:
                return False, "End date cannot be before start date"

            return True, ""
        except ValueError as e:
            return False, f"Invalid date format: {str(e)}"

    @staticmethod
    def validate_time_range(start_time: str, end_time: str, time_format: str = "%H:%M") -> Tuple[bool, str]:
        """
        Validate time range (end time must be >= start time)

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            start = datetime.strptime(start_time, time_format).time()
            end = datetime.strptime(end_time, time_format).time()

            if end < start:
                return False, "End time cannot be before start time"

            return True, ""
        except ValueError as e:
            return False, f"Invalid time format: {str(e)}"

    @staticmethod
    def validate_activity_data(activity_data: Dict[str, Any]) -> List[str]:
        """
        Validate activity data

        Returns:
            List of validation error messages
        """
        errors = []

        # Required fields
        required_fields = ['activity_type', 'start_date']
        for field in required_fields:
            if not activity_data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")

        # Validate date format
        start_date = activity_data.get('start_date')
        if start_date and not ValidationService.validate_date(start_date):
            errors.append("Invalid start date format")

        end_date = activity_data.get('end_date')
        if end_date and not ValidationService.validate_date(end_date):
            errors.append("Invalid end date format")

        # Validate date range
        if start_date and end_date:
            is_valid, error_msg = ValidationService.validate_date_range(start_date, end_date)
            if not is_valid:
                errors.append(error_msg)

        # Validate time format
        start_time = activity_data.get('start_time')
        if start_time and not ValidationService.validate_time(start_time):
            errors.append("Invalid start time format")

        end_time = activity_data.get('end_time')
        if end_time and not ValidationService.validate_time(end_time):
            errors.append("Invalid end time format")

        # Validate time range (only if dates are the same)
        if start_date == end_date and start_time and end_time:
            is_valid, error_msg = ValidationService.validate_time_range(start_time, end_time)
            if not is_valid:
                errors.append(error_msg)

        # Validate text field lengths
        text_limits = {
            'venue': 200,
            'collaboration_sponsor': 500,
            'highlights': 2000,
            'key_takeaway': 2000,
            'summary': 3000,
            'follow_up_plan': 2000
        }

        for field, max_length in text_limits.items():
            value = activity_data.get(field, '')
            if value and len(value) > max_length:
                errors.append(f"{field.replace('_', ' ').title()} exceeds maximum length of {max_length} characters")

        # Validate sub category
        sub_category = activity_data.get('sub_category')
        sub_category_other = activity_data.get('sub_category_other')

        if sub_category == 'Other' and not sub_category_other:
            errors.append("Please specify sub category when 'Other' is selected")

        return errors

    @staticmethod
    def validate_speaker_data(speaker_data: Dict[str, Any]) -> List[str]:
        """
        Validate speaker data

        Returns:
            List of validation error messages
        """
        errors = []

        # Required fields
        if not speaker_data.get('name'):
            errors.append("Speaker name is required")

        # Validate text field lengths
        text_limits = {
            'name': 100,
            'title_position': 100,
            'organization': 150,
            'contact_info': 200,
            'presentation_title': 200
        }

        for field, max_length in text_limits.items():
            value = speaker_data.get(field, '')
            if value and len(value) > max_length:
                field_display = field.replace('_', ' ').title()
                errors.append(f"{field_display} exceeds maximum length of {max_length} characters")

        # Validate contact info if provided
        contact_info = speaker_data.get('contact_info')
        if contact_info:
            # Basic validation - check if it looks like email or phone
            if not (ValidationService.validate_email(contact_info) or
                   ValidationService.validate_phone_number(contact_info)):
                errors.append("Contact information should be a valid email address or phone number")

        return errors

    @staticmethod
    def validate_participant_data(participant_data: Dict[str, Any]) -> List[str]:
        """
        Validate participant data

        Returns:
            List of validation error messages
        """
        errors = []

        # Required fields
        if not participant_data.get('participant_type'):
            errors.append("Participant type is required")

        count = participant_data.get('count', 0)
        if not isinstance(count, int) or count <= 0:
            errors.append("Participant count must be a positive integer")

        if count > 9999:
            errors.append("Participant count cannot exceed 9999")

        return errors

    @staticmethod
    def validate_report_preparer_data(preparer_data: Dict[str, Any]) -> List[str]:
        """
        Validate report preparer data

        Returns:
            List of validation error messages
        """
        errors = []

        # Required fields
        if not preparer_data.get('name'):
            errors.append("Preparer name is required")

        if not preparer_data.get('designation'):
            errors.append("Preparer designation is required")

        # Validate text field lengths
        text_limits = {
            'name': 100,
            'designation': 100
        }

        for field, max_length in text_limits.items():
            value = preparer_data.get(field, '')
            if value and len(value) > max_length:
                field_display = field.replace('_', ' ').title()
                errors.append(f"{field_display} exceeds maximum length of {max_length} characters")

        return errors

    @staticmethod
    def validate_complete_activity_report(complete_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete activity report data

        Returns:
            Dict with validation results containing:
            - valid: bool
            - errors: List of error messages
            - warnings: List of warning messages
        """
        errors = []
        warnings = []

        # Validate activity data
        activity = complete_data.get('activity', {})
        activity_errors = ValidationService.validate_activity_data(activity)
        errors.extend(activity_errors)

        # Validate speakers
        speakers = complete_data.get('speakers', [])
        if len(speakers) == 0:
            errors.append("At least one speaker is required")
        else:
            for i, speaker in enumerate(speakers, 1):
                speaker_errors = ValidationService.validate_speaker_data(speaker)
                for error in speaker_errors:
                    errors.append(f"Speaker {i}: {error}")

        # Validate participants
        participants = complete_data.get('participants', [])
        if len(participants) == 0:
            errors.append("At least one participant type is required")
        else:
            for i, participant in enumerate(participants, 1):
                participant_errors = ValidationService.validate_participant_data(participant)
                for error in participant_errors:
                    errors.append(f"Participant Type {i}: {error}")

        # Validate report preparers
        preparers = complete_data.get('report_preparers', [])
        if len(preparers) == 0:
            errors.append("At least one report preparer is required")
        else:
            for i, preparer in enumerate(preparers, 1):
                preparer_errors = ValidationService.validate_report_preparer_data(preparer)
                for error in preparer_errors:
                    errors.append(f"Report Preparer {i}: {error}")

        # Validate photos (for PDF generation)
        photos = complete_data.get('photos', [])
        if len(photos) < 2:
            warnings.append(f"Only {len(photos)} photo(s) uploaded. Minimum 2 recommended for PDF generation")

        # Check for missing optional but recommended fields
        if not activity.get('venue'):
            warnings.append("Venue not specified - recommended for complete report")

        if not activity.get('highlights') and not activity.get('summary'):
            warnings.append("No highlights or summary provided - recommended for complete report")

        if not activity.get('key_takeaway'):
            warnings.append("No key takeaways provided - recommended for complete report")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    @staticmethod
    def sanitize_text_input(text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize text input by removing potentially harmful characters

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Remove potentially problematic characters for database
        sanitized = text.strip()

        # Remove null characters
        sanitized = sanitized.replace('\x00', '')

        # Limit length if specified
        if max_length:
            sanitized = sanitized[:max_length]

        return sanitized

    @staticmethod
    def validate_file_upload(file_path: str, allowed_extensions: List[str], max_size_mb: int) -> Dict[str, Any]:
        """
        Validate uploaded file

        Returns:
            Dict with validation results
        """
        import os

        errors = []

        # Check if file exists
        if not os.path.exists(file_path):
            return {
                'valid': False,
                'errors': ['File does not exist']
            }

        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in [ext.lower() for ext in allowed_extensions]:
            errors.append(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")

        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            errors.append(f"File size exceeds {max_size_mb}MB limit")

        # Additional validation for image files
        if file_ext in ['.jpg', '.jpeg', '.png']:
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    # Verify it's a valid image
                    img.verify()
            except Exception:
                errors.append("Invalid or corrupted image file")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'file_size_mb': round(file_size_mb, 2)
        }