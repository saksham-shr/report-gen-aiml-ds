"""
Complete PDF generation service using WeasyPrint
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

        return {
            'university_name': UNIVERSITY_INFO['name'],
            'school_name': UNIVERSITY_INFO['school'],
            'department_name': UNIVERSITY_INFO['department'],
            'activity': activity,
            'speakers': enhanced_speakers,
            'participants': enhanced_participants,
            'report_preparers': report_preparers,
            'photos': photos,
            'options': options,
            'generation_date': datetime.now().strftime("%d %B %Y")
        }

    def render_template(self, template_data: Dict[str, Any]) -> str:
        """Render HTML template with data"""
        try:
            template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Activity Report - {{ university_name }}</title>
    <style>
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
            font-size: 12pt;
            line-height: 1.2;
            color: black;
            background: white;
            margin: 0;
            padding: 0;
        }

        /* University Header Styles */
        .university-header {
            text-align: center;
            margin-bottom: 30pt;
        }

        .university-title {
            font-size: 14pt;
            font-weight: bold;
            line-height: 1.2;
            margin-bottom: 5pt;
        }

        /* Main Heading */
        .main-heading {
            font-size: 16pt;
            font-weight: bold;
            text-align: center;
            text-transform: uppercase;
            text-decoration: underline;
            margin-bottom: 14pt;
        }

        /* Section Styles */
        .section-title {
            font-size: 14pt;
            font-weight: bold;
            text-align: center;
            text-decoration: underline;
            margin-bottom: 10pt;
        }

        /* Field Styles */
        .field-label {
            font-size: 12pt;
            font-weight: bold;
            text-align: left;
            margin-bottom: 6pt;
        }

        .field-value {
            font-size: 12pt;
            text-align: left;
            margin-bottom: 6pt;
        }

        /* Paragraph Styles */
        .paragraph {
            font-size: 12pt;
            text-align: justify;
            line-height: 1.15;
            margin-bottom: 6pt;
        }
    </style>
</head>
<body>

    <!-- University Header -->
    <div class="university-header">
        <div class="university-title">{{ university_name }}</div>
        <div class="university-title">{{ school_name }}</div>
        <div class="university-title">{{ department_name }}</div>
    </div>

    <br><br>

    <!-- Main Heading -->
    <div class="main-heading">Activity Report</div>

    <br><br>

    <!-- General Information -->
    <div class="section-title">General Information</div>

    <div class="field-label">Type of Activity:</div>
    <div class="field-value">{{ activity.activity_type }}</div>

    <div class="field-label">Date:</div>
    <div class="field-value">{{ activity.start_date }}</div>

    {% if activity.venue %}
    <div class="field-label">Venue:</div>
    <div class="field-value">{{ activity.venue }}</div>
    {% endif %}

    <!-- Speakers -->
    {% if speakers %}
    <div class="section-title">Speaker Details</div>
    {% for speaker in speakers %}
    <div class="field-label">{{ loop.index }}. {{ speaker.name }}</div>
    {% if speaker.title_position or speaker.organization %}
    <div class="field-value">
        {% if speaker.title_position %}{{ speaker.title_position }}{% endif %}
        {% if speaker.title_position and speaker.organization %}, {% endif %}
        {% if speaker.organization %}{{ speaker.organization }}{% endif %}
    </div>
    {% endif %}
    <br>
    {% endfor %}
    {% endif %}

    <!-- Participants -->
    {% if participants %}
    <div class="section-title">Participants Profile</div>
    {% for participant in participants %}
    <div class="field-value">{{ participant.count }} {{ participant.display_type }}</div>
    {% endfor %}
    {% endif %}

</body>
</html>
            """
            
            template = Template(template_str)
            return template.render(**template_data)

        except Exception as e:
            raise Exception(f"Template rendering error: {str(e)}")

    def process_images(self, html_content: str, temp_dir: str) -> str:
        """Process and optimize images for PDF generation"""
        # For now, just return the HTML content
        # In a full implementation, this would process images
        return html_content

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

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }