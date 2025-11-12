# Academic Activity Report Generator

A desktop application for generating standardized activity reports for Christ (Deemed to be University), School of Engineering and Technology, Department of AI, ML & Data Science.

## Features

### Form Management
- **8 Complete Form Sections** with dynamic controls
- **General Information**: Activity types, subcategories, date/time pickers
- **Speaker Details**: Dynamic speaker sections with validation
- **Participants Profile**: Multi-type participant management
- **Synopsis**: Rich text areas for highlights and summaries
- **Report Prepared By**: Digital signature support
- **Speaker Profiles**: Image uploads with profile text
- **Activity Photos**: Drag-and-drop photo management (min 2 required)
- **PDF Generation**: Complete report generation with validation

### Data Management
- **SQLite Database**: Local storage with full schema
- **Auto-save Functionality**: Every 30 seconds
- **Data Validation**: Comprehensive form validation
- **File Management**: Organized image and file storage
- **Backup System**: JSON backup capabilities

### PDF Generation
- **WeasyPrint Integration**: Professional PDF generation
- **University Formatting**: Exact university specifications
- **Image Optimization**: Automatic image processing
- **Customizable Options**: Include/exclude sections
- **Template-based**: Jinja2 HTML template system

## Installation

### Prerequisites
- Python 3.9 or higher
- WeasyPrint system dependencies

### System Dependencies (WeasyPrint)

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libgdk-pixbuf2.0-0

# For WeasyPrint
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# For JPEG/PNG support
sudo apt-get install libjpeg-dev libopenjp2-7-dev libtiff5-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev
```

#### macOS:
```bash
brew install pango cairo gdk-pixbuf libffi
```

#### Windows:
WeasyPrint provides installers that include all dependencies.

### Application Setup

1. **Clone or download the project**
2. **Navigate to project directory**
   ```bash
   cd report-gen-aiml-ds
   ```

3. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python src/main.py
   ```

## Usage

### Creating a New Activity Report

1. **Launch the application**
2. **Navigate through the 8 form sections** using the sidebar:
   - 📋 **General Information**: Select activity type, dates, venue
   - 👤 **Speaker Details**: Add one or more speakers with their details
   - 👥 **Participants**: Add participant types and counts
   - 📝 **Synopsis**: Write highlights, key takeaways, and summary
   - ✍️ **Report Prepared By**: Add preparers with digital signatures
   - 🔊 **Speaker Profiles**: Upload speaker photos and add profiles
   - 📷 **Activity Photos**: Upload at least 2 activity photos
   - 📄 **Generate PDF**: Validate and generate final report

3. **Auto-save**: Your data is automatically saved every 30 seconds
4. **Manual Save**: Use the save button in each section to save immediately
5. **PDF Generation**: Once all sections are complete, generate the final PDF

### Activity Types Supported
- Seminar
- Workshop
- Conference
- Technical Talk
- Guest Talk
- Industry Visit
- Sports
- Cultural Competition
- Technical/Academic Fest
- CAADS
- Research Clubs
- Newsletter
- Alumni Event
- Faculty Development Program
- Quality Improvement Program
- Refresher Course
- MoU
- Outreach Activity
- International Event

### Sub Categories
- Competitive Exam
- Career Guidance
- Skill Development
- Communication Skills
- Women Event
- Emerging Trends and Technology
- Life Skills
- Soft Skills
- Other (custom option)

## Project Structure

```
report-gen-aiml-ds/
├── src/
│   ├── main.py                 # Application entry point
│   ├── ui/                     # User interface components
│   │   ├── main_window.py      # Main window with sidebar
│   │   ├── forms/              # Form sections
│   │   │   ├── general_info.py
│   │   │   ├── speaker_details.py
│   │   │   ├── participants.py
│   │   │   ├── synopsis.py
│   │   │   ├── report_prepared_by.py
│   │   │   ├── speaker_profile.py
│   │   │   └── activity_photos.py
│   │   └── widgets/            # Custom UI widgets
│   │       └── sidebar.py
│   ├── models/                 # Data models
│   │   ├── activity.py
│   │   ├── speaker.py
│   │   ├── participant.py
│   │   └── report.py
│   ├── services/               # Business logic
│   │   ├── database.py         # SQLite operations
│   │   ├── pdf_generator.py    # WeasyPrint PDF creation
│   │   ├── file_manager.py     # Image/file handling
│   │   └── validation.py       # Form validation
│   ├── templates/              # HTML templates for PDF
│   │   ├── report_template.html
│   │   └── styles.css
│   └── utils/                  # Utility functions
│       ├── constants.py        # Activity types, limits
│       └── helpers.py
├── data/
│   ├── reports.db              # SQLite database
│   ├── backups/                # JSON backup files
│   ├── images/                 # Uploaded activity photos
│   └── signatures/             # Digital signatures
├── generated_pdfs/             # Generated PDF reports
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Data Storage

### Database Schema
- **activities**: Main activity information
- **speakers**: Speaker details and profiles
- **participants**: Participant types and counts
- **report_preparers**: Report preparer information
- **activity_photos**: Photo metadata and paths

### File Organization
```
data/
├── images/
│   ├── activities/[activity_id]/
│   └── speakers/
├── signatures/
└── backups/
```

## PDF Specifications

The generated PDFs follow exact university formatting requirements:

### Document Settings
- **Paper Size**: A4 (8.27 x 11.69 inches)
- **Margins**: 1 inch (Top, Bottom, Left, Right)
- **Orientation**: Portrait
- **Font**: Times New Roman
- **Font Sizes**: 12pt (body), 14pt (section titles), 16pt (main title)
- **Line Spacing**: 1.15 to 1.2
- **Footer**: "Page X of Y", centered, 10pt font

### Content Structure
1. **University Header Block**
2. **General Information**
3. **Speaker Details**
4. **Participants Profile**
5. **Synopsis** (Highlights, Key Takeaways, Summary, Follow-up Plan)
6. **Report Prepared By**
7. **Speaker Profiles** (Optional)
8. **Activity Photos** (2 per page)

## Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **RAM**: 4GB
- **Disk Space**: 1GB free
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

### Recommended Requirements
- **Python**: 3.10 or higher
- **RAM**: 8GB
- **Disk Space**: 2GB free
- **Display**: 1920x1080 or higher

## Troubleshooting

### Common Issues

#### WeasyPrint Installation Issues
If you encounter WeasyPrint installation errors, ensure all system dependencies are installed (see Prerequisites section).

#### Image Upload Issues
- Ensure images are in JPG or PNG format
- Check file size limits (5MB for activity photos, 5MB for speaker profiles, 2MB for signatures)
- Verify images are not corrupted

#### PDF Generation Issues
- Ensure all required form sections are completed
- Check that at least 2 activity photos are uploaded
- Verify all speakers have names
- Make sure at least one report preparer is added

#### Database Issues
- The application automatically creates the SQLite database on first run
- Database file location: `data/reports.db`
- Backups are automatically created in `data/backups/`

### Error Messages
- **"No Activity Found"**: Save general information first before accessing other sections
- **"Validation Error"**: Complete all required fields marked with *
- **"File Too Large"**: Reduce image size or compress before uploading
- **"PDF Generation Failed"**: Check console output for detailed error information

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
This project follows PEP 8 guidelines. Use a code formatter like black for consistency.

### Adding New Features
1. Follow the existing pattern for forms (create in `src/ui/forms/`)
2. Add database models in `src/models/`
3. Update constants in `src/utils/constants.py`
4. Add validation rules in `src/services/validation.py`

## Support

For technical support or questions:
1. Check this README for common solutions
2. Review the error messages in the application console
3. Ensure all system dependencies are properly installed

## License

This project is developed for Christ (Deemed to be University), Department of AI, ML & Data Science.

## Version History

### v1.0.0 (Current)
- Complete 8-section form system
- SQLite database integration
- PDF generation with WeasyPrint
- Image upload and management
- Auto-save functionality
- Comprehensive validation
- University formatting compliance