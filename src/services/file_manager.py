"""
Complete File management service
"""

import os
import shutil
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from PIL import Image
import hashlib

class FileManagerService:
    """Service for managing file operations including uploads, storage, and organization"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(__file__), '../../data')

        self.base_dir = Path(base_dir)
        self.setup_directories()

    def setup_directories(self):
        """Create necessary directory structure"""
        directories = [
            'images/activities',
            'images/speakers',
            'signatures',
            'backups',
            'temp'
        ]

        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_directory_path(self, file_type: str, activity_id: Optional[int] = None) -> Path:
        """Get appropriate directory path for file type"""
        base_path = self.base_dir

        if file_type == 'activity_photo':
            if activity_id:
                return base_path / 'images/activities' / str(activity_id)
            else:
                return base_path / 'temp'

        elif file_type == 'speaker_profile':
            return base_path / 'images/speakers'

        elif file_type == 'signature':
            return base_path / 'signatures'

        else:
            return base_path / 'temp'

    def generate_unique_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate unique filename while preserving extension"""
        name, ext = os.path.splitext(original_filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]

        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}{ext}"
        else:
            return f"{timestamp}_{unique_id}{ext}"

    def validate_image_file(self, file_path: str, max_size_mb: int = 5) -> Dict[str, Any]:
        """
        Validate image file

        Returns:
            Dict with validation results
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'valid': False,
                    'error': 'File does not exist'
                }

            # Check file size
            file_size = os.path.getsize(file_path)
            max_size_bytes = max_size_mb * 1024 * 1024

            if file_size > max_size_bytes:
                return {
                    'valid': False,
                    'error': f'File size exceeds {max_size_mb}MB limit'
                }

            # Check if it's a valid image
            try:
                with Image.open(file_path) as img:
                    img.verify()
            except Exception:
                return {
                    'valid': False,
                    'error': 'Invalid image file format'
                }

            # Reopen to get image properties (verify() closes the file)
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format

            return {
                'valid': True,
                'width': width,
                'height': height,
                'format': format_name,
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2)
            }

        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }

    def save_uploaded_file(self, source_path: str, file_type: str, activity_id: Optional[int] = None) -> Optional[str]:
        """
        Save uploaded file to appropriate location

        Returns:
            str: Path where file was saved, or None if failed
        """
        try:
            # Get target directory
            target_dir = self.get_directory_path(file_type, activity_id)
            target_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            original_name = os.path.basename(source_path)
            prefix = self.get_prefix_for_file_type(file_type, activity_id)
            unique_filename = self.generate_unique_filename(original_name, prefix)

            # Copy file to target location
            target_path = target_dir / unique_filename
            shutil.copy2(source_path, target_path)

            return str(target_path)

        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return None

    def get_prefix_for_file_type(self, file_type: str, activity_id: Optional[int] = None) -> str:
        """Get prefix for filename based on file type"""
        prefixes = {
            'activity_photo': 'photo',
            'speaker_profile': 'speaker',
            'signature': 'signature'
        }

        base_prefix = prefixes.get(file_type, 'file')

        if activity_id and file_type == 'activity_photo':
            return f"{base_prefix}_{activity_id}"
        elif activity_id and file_type == 'speaker_profile':
            return f"{base_prefix}_{activity_id}"

        return base_prefix