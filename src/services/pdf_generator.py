"""
PDF generation service using WeasyPrint
"""

import os
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any, Optional
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from jinja2 import Environment, FileSystemLoader, Template
from PIL import Image

from ..utils.constants import UNIVERSITY_INFO

class PDFGeneratorService:
    """Service for generating PDF reports using WeasyPrint"""

    def __init__(self, template_dir: str = None):
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), '../templates')

        self.template_dir = template_dir
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )

        # Add custom filters
        self.jinja_env.filters['nl2br'] = self.nl2br_filter
        self.jinja_env.filters['date'] = self.date_filter

        # Font configuration
        self.font_config = FontConfiguration()

    def nl2br_filter(self, text):
        """Convert newlines to <br> tags"""
        if not text:
            return ""
        return text.replace('\n', '<br>')

    def date_filter(self, date_str, format_str="j F Y"):
        """Format date string"""
        if not date_str:
            return ""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime(format_str)
        except:
            return date_str

    def generate_pdf(self, activity_data: Dict[str, Any], output_path: str, options: Dict[str, Any] = None) -> bool:
        """
        Generate PDF report for activity

        Args:
            activity_data: Complete activity data including all related tables
            output_path: Path where PDF should be saved
            options: PDF generation options

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Set default options
            if options is None:
                options = {
                    'include_photos': True,
                    'include_profiles': True,
                    'include_signatures': True,
                    'add_watermark': True,
                    'add_page_numbers': True
                }

            # Prepare template data
            template_data = self.prepare_template_data(activity_data, options)

            # Generate HTML from template
            html_content = self.render_template(template_data)

            # Create temporary directory for image processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Process images and update HTML
                html_content = self.process_images(html_content, temp_dir)

                # Generate PDF
                self.create_pdf_from_html(html_content, output_path)

            return True

        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return False

    def prepare_template_data(self, activity_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        activity = activity_data.get('activity', {})
        speakers = activity_data.get('speakers', [])
        participants = activity_data.get('participants', [])
        report_preparers = activity_data.get('report_preparers', [])
        photos = activity_data.get('photos', [])

        # Enhance speaker data
        enhanced_speakers = []
        for speaker in speakers:
            enhanced_speaker = dict(speaker)
            enhanced_speaker['display_name'] = speaker.get('name', '')
            enhanced_speakers.append(enhanced_speaker)

        # Enhance participant data
        enhanced_participants = []
        for participant in participants:
            enhanced_participant = dict(participant)
            participant_type = participant.get('participant_type', '')
            enhanced_participant['display_type'] = {
                'faculty': 'Faculty',
                'student': 'Students',
                'research_scholar': 'Research Scholars'
            }.get(participant_type, participant_type.title())
            enhanced_participants.append(enhanced_participant)

        # Format dates in activity data
        if activity.get('start_date'):
            try:
                start_date = datetime.strptime(activity['start_date'], "%Y-%m-%d")
                activity['start_date_formatted'] = start_date.strftime("%d %B %Y")
                if activity.get('end_date'):
                    end_date = datetime.strptime(activity['end_date'], "%Y-%m-%d")
                    activity['end_date_formatted'] = end_date.strftime("%d %B %Y")
            except:
                pass

        # Process photos (limit to reasonable number for PDF)
        processed_photos = photos[:10] if options.get('include_photos', True) else []

        return {
            'university_name': UNIVERSITY_INFO['name'],
            'school_name': UNIVERSITY_INFO['school'],
            'department_name': UNIVERSITY_INFO['department'],
            'activity': activity,
            'speakers': enhanced_speakers,
            'participants': enhanced_participants,
            'report_preparers': report_preparers,
            'photos': processed_photos,
            'options': options,
            'generation_date': datetime.now().strftime("%d %B %Y")
        }

    def render_template(self, template_data: Dict[str, Any]) -> str:
        """Render HTML template with data"""
        try:
            template = self.jinja_env.get_template('report_template.html')
            return template.render(**template_data)
        except Exception as e:
            raise Exception(f"Template rendering error: {str(e)}")

    def process_images(self, html_content: str, temp_dir: str) -> str:
        """Process and optimize images for PDF generation"""
        import re
        from urllib.parse import urlparse

        # Find all image src attributes
        img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
        matches = re.findall(img_pattern, html_content)

        for img_src in matches:
            try:
                if img_src.startswith(('http://', 'https://')):
                    # Download remote images
                    processed_path = self.download_and_process_image(img_src, temp_dir)
                elif os.path.isabs(img_src):
                    # Process local images
                    processed_path = self.process_local_image(img_src, temp_dir)
                else:
                    # Skip data URLs or other formats
                    continue

                if processed_path:
                    # Replace image src with processed image
                    html_content = html_content.replace(img_src, processed_path)

            except Exception as e:
                print(f"Warning: Failed to process image {img_src}: {str(e)}")
                continue

        return html_content

    def download_and_process_image(self, url: str, temp_dir: str) -> Optional[str]:
        """Download and process remote image"""
        try:
            import requests

            # Download image
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Save to temp file
            temp_file = os.path.join(temp_dir, f"remote_{hash(url)}.jpg")
            with open(temp_file, 'wb') as f:
                f.write(response.content)

            # Process and optimize
            return self.process_local_image(temp_file, temp_dir)

        except:
            return None

    def process_local_image(self, image_path: str, temp_dir: str) -> Optional[str]:
        """Process and optimize local image for PDF"""
        try:
            if not os.path.exists(image_path):
                return None

            # Open image
            img = Image.open(image_path)

            # Convert to RGB if necessary (for PDF compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img

            # Optimize image size for PDF
            max_width = 800
            max_height = 600

            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Save optimized image
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)
            processed_path = os.path.join(temp_dir, f"processed_{name}.jpg")

            img.save(processed_path, 'JPEG', quality=85, optimize=True)
            return processed_path

        except Exception as e:
            print(f"Warning: Failed to process image {image_path}: {str(e)}")
            return None

    def create_pdf_from_html(self, html_content: str, output_path: str):
        """Create PDF from HTML content using WeasyPrint"""
        try:
            # Create HTML object
            html = HTML(string=html_content)

            # Create CSS for PDF formatting
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 1in;
                    @bottom-center {
                        content: "Page " counter(page) " of " counter(pages);
                        font-size: 10pt;
                        font-family: "Times New Roman", serif;
                    }
                }
                body {
                    font-family: "Times New Roman", serif;
                }
            ''')

            # Generate PDF
            html.write_pdf(
                output_path,
                stylesheets=[css],
                font_config=self.font_config
            )

        except Exception as e:
            raise Exception(f"PDF creation error: {str(e)}")

    def preview_pdf(self, activity_data: Dict[str, Any], options: Dict[str, Any] = None) -> str:
        """
        Generate HTML preview of the report

        Returns:
            str: HTML content for preview
        """
        try:
            # Set default options
            if options is None:
                options = {
                    'include_photos': True,
                    'include_profiles': True,
                    'include_signatures': True,
                    'add_watermark': False
                }

            # Prepare template data
            template_data = self.prepare_template_data(activity_data, options)

            # Generate HTML from template
            return self.render_template(template_data)

        except Exception as e:
            raise Exception(f"Preview generation error: {str(e)}")

    def validate_requirements(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate activity data meets minimum requirements for PDF generation

        Returns:
            Dict with validation results
        """
        errors = []
        warnings = []

        activity = activity_data.get('activity', {})
        speakers = activity_data.get('speakers', [])
        participants = activity_data.get('participants', [])
        photos = activity_data.get('photos', [])
        report_preparers = activity_data.get('report_preparers', [])

        # Check required fields
        if not activity.get('activity_type'):
            errors.append("Activity type is required")

        if not activity.get('start_date'):
            errors.append("Start date is required")

        # Check speakers
        if len(speakers) == 0:
            errors.append("At least one speaker is required")
        else:
            for i, speaker in enumerate(speakers, 1):
                if not speaker.get('name'):
                    errors.append(f"Speaker {i}: Name is required")

        # Check participants
        if len(participants) == 0:
            errors.append("At least one participant type is required")
        else:
            for participant in participants:
                if not participant.get('count', 0) > 0:
                    errors.append("All participant counts must be greater than 0")

        # Check report preparers
        if len(report_preparers) == 0:
            errors.append("At least one report preparer is required")
        else:
            for preparer in report_preparers:
                if not preparer.get('name'):
                    errors.append("All report preparers must have names")

        # Check photos (warnings for now, as per planning minimum is 2)
        if len(photos) < 2:
            warnings.append(f"Only {len(photos)} photo(s) uploaded. Minimum 2 recommended for best report quality")

        # Check for missing optional but recommended fields
        if not activity.get('venue'):
            warnings.append("Venue not specified - recommended for complete report")

        if not activity.get('highlights') and not activity.get('summary'):
            warnings.append("No highlights or summary provided - recommended for complete report")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }