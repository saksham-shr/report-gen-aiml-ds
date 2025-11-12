"""
File management service for handling images and files
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

    def optimize_image_for_pdf(self, image_path: str, output_path: Optional[str] = None) -> str:
        """
        Optimize image for PDF generation

        Returns:
            str: Path to optimized image
        """
        try:
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_optimized{ext}"

            # Open image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img

                # Resize for PDF (reasonable dimensions)
                max_width = 1200
                max_height = 900

                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                # Save with compression
                img.save(output_path, 'JPEG', quality=85, optimize=True)

            return output_path

        except Exception as e:
            print(f"Error optimizing image: {str(e)}")
            return image_path  # Return original if optimization fails

    def create_backup(self, activity_id: int, activity_data: Dict[str, Any]) -> str:
        """
        Create backup of activity data

        Returns:
            str: Path to backup file
        """
        try:
            import json

            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"activity_{activity_id}_backup_{timestamp}.json"
            backup_path = self.base_dir / 'backups' / backup_filename

            # Create backup data
            backup_data = {
                'activity_id': activity_id,
                'timestamp': timestamp,
                'data': activity_data,
                'version': '1.0'
            }

            # Save backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            return str(backup_path)

        except Exception as e:
            print(f"Error creating backup: {str(e)}")
            return ""

    def restore_backup(self, backup_path: str) -> Optional[Dict[str, Any]]:
        """
        Restore activity data from backup

        Returns:
            Dict with activity data, or None if failed
        """
        try:
            import json

            if not os.path.exists(backup_path):
                return None

            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            return backup_data.get('data')

        except Exception as e:
            print(f"Error restoring backup: {str(e)}")
            return None

    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        try:
            temp_dir = self.base_dir / 'temp'
            if not temp_dir.exists():
                return

            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

            for file_path in temp_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                    except Exception as e:
                        print(f"Error deleting temp file {file_path}: {str(e)}")

        except Exception as e:
            print(f"Error during temp file cleanup: {str(e)}")

    def get_file_hash(self, file_path: str) -> str:
        """Get SHA256 hash of file for integrity checking"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""

    def verify_file_integrity(self, file_path: str, expected_hash: str) -> bool:
        """Verify file integrity using hash"""
        try:
            actual_hash = self.get_file_hash(file_path)
            return actual_hash == expected_hash
        except Exception:
            return False

    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about storage usage"""
        try:
            storage_info = {}

            # Calculate sizes for different directories
            directories = ['images/activities', 'images/speakers', 'signatures', 'backups']

            for directory in directories:
                dir_path = self.base_dir / directory
                total_size = 0
                file_count = 0

                if dir_path.exists():
                    for file_path in dir_path.rglob('*'):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
                            file_count += 1

                storage_info[directory.replace('/', '_')] = {
                    'size_bytes': total_size,
                    'size_mb': round(total_size / (1024 * 1024), 2),
                    'file_count': file_count
                }

            # Total storage
            total_size = sum(info['size_bytes'] for info in storage_info.values())
            storage_info['total'] = {
                'size_bytes': total_size,
                'size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': sum(info['file_count'] for info in storage_info.values())
            }

            return storage_info

        except Exception as e:
            print(f"Error getting storage info: {str(e)}")
            return {}

    def delete_activity_files(self, activity_id: int):
        """Delete all files associated with an activity"""
        try:
            # Delete activity photos
            activity_photos_dir = self.base_dir / 'images/activities' / str(activity_id)
            if activity_photos_dir.exists():
                shutil.rmtree(activity_photos_dir)

            # TODO: Also delete related speaker profiles and signatures
            # This would require database lookup to find associated files

        except Exception as e:
            print(f"Error deleting activity files: {str(e)}")

    def export_activity_files(self, activity_id: int, export_path: str) -> bool:
        """
        Export all files for an activity to a zip file

        Returns:
            bool: True if successful
        """
        try:
            import zipfile

            activity_photos_dir = self.base_dir / 'images/activities' / str(activity_id)
            if not activity_photos_dir.exists():
                return False

            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in activity_photos_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(activity_photos_dir)
                        zipf.write(file_path, arcname)

            return True

        except Exception as e:
            print(f"Error exporting activity files: {str(e)}")
            return False