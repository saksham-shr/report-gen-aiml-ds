"""
Complete Speaker Details Form
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QFormLayout, QGroupBox, QScrollArea,
    QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ...utils.constants import TEXT_LIMITS, SECTION_LIMITS

class SpeakerWidget(QWidget):
    """Individual speaker widget"""

    remove_requested = pyqtSignal()

    def __init__(self, speaker_number=1):
        super().__init__()
        self.speaker_number = speaker_number
        self.setup_ui()

    def setup_ui(self):
        """Setup speaker widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header with remove button
        header_layout = QHBoxLayout()
        title_label = QLabel(f"Speaker {self.speaker_number}")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title_label)

        self.remove_button = QPushButton("Remove")
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.remove_button.clicked.connect(self.remove_requested.emit)
        header_layout.addWidget(self.remove_button)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Speaker form
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(8)

        # Name (required)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter speaker name")
        self.name_edit.setMaxLength(TEXT_LIMITS["speaker_name"])
        form_layout.addRow("Name *:", self.name_edit)

        # Title/Position
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter title/position")
        self.title_edit.setMaxLength(TEXT_LIMITS["title_position"])
        form_layout.addRow("Title/Position:", self.title_edit)

        # Organization
        self.organization_edit = QLineEdit()
        self.organization_edit.setPlaceholderText("Enter organization")
        self.organization_edit.setMaxLength(TEXT_LIMITS["organization"])
        form_layout.addRow("Organization:", self.organization_edit)

        # Contact Info
        self.contact_edit = QLineEdit()
        self.contact_edit.setPlaceholderText("Enter contact information")
        self.contact_edit.setMaxLength(TEXT_LIMITS["contact_info"])
        form_layout.addRow("Contact Info:", self.contact_edit)

        # Title of Presentation
        self.presentation_title_edit = QLineEdit()
        self.presentation_title_edit.setPlaceholderText("Enter presentation title")
        self.presentation_title_edit.setMaxLength(TEXT_LIMITS["presentation_title"])
        form_layout.addRow("Title of Presentation:", self.presentation_title_edit)

        layout.addWidget(form_widget)

        # Set widget style
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin: 5px;
            }
        """)

    def get_data(self):
        """Get speaker data"""
        return {
            'name': self.name_edit.text().strip(),
            'title_position': self.title_edit.text().strip() or None,
            'organization': self.organization_edit.text().strip() or None,
            'contact_info': self.contact_edit.text().strip() or None,
            'presentation_title': self.presentation_title_edit.text().strip() or None
        }

    def set_data(self, data):
        """Set speaker data"""
        self.name_edit.setText(data.get('name', ''))
        self.title_edit.setText(data.get('title_position', ''))
        self.organization_edit.setText(data.get('organization', ''))
        self.contact_edit.setText(data.get('contact_info', ''))
        self.presentation_title_edit.setText(data.get('presentation_title', ''))

    def is_valid(self):
        """Check if speaker data is valid"""
        return bool(self.name_edit.text().strip())

class SpeakerDetailsForm(QWidget):
    """Speaker Details form"""

    data_changed = pyqtSignal()

    def __init__(self, db_service, activity_id=None):
        super().__init__()
        self.db_service = db_service
        self.activity_id = activity_id
        self.speaker_widgets = []
        self.next_speaker_number = 1

        self.setup_ui()
        self.setup_connections()

        if activity_id:
            self.load_data()

    def setup_ui(self):
        """Setup the form UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # Form container
        form_container = QFrame()
        form_container.setFrameStyle(QFrame.Box)
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_container)

        # Form title
        title_label = QLabel("Speaker Details")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        form_layout.addWidget(title_label)

        # Instructions
        instructions = QLabel("Add details for each speaker presenting at the activity. At least one speaker is required.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 15px;")
        form_layout.addWidget(instructions)

        # Add speaker button
        self.add_speaker_button = QPushButton("Add Another Speaker")
        self.add_speaker_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.add_speaker_button.clicked.connect(self.add_speaker)
        form_layout.addWidget(self.add_speaker_button)

        # Speakers container with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: 1px solid #ecf0f1;
                border-radius: 5px;
            }
        """)

        self.speakers_container = QWidget()
        self.speakers_layout = QVBoxLayout(self.speakers_container)
        self.speakers_layout.setSpacing(10)
        self.speakers_layout.addStretch()

        scroll.setWidget(self.speakers_container)
        form_layout.addWidget(scroll)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        self.save_button = QPushButton("Save Speakers")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.save_button.clicked.connect(self.save_data)
        actions_layout.addWidget(self.save_button)

        form_layout.addLayout(actions_layout)
        main_layout.addWidget(form_container)

        # Add initial speaker
        self.add_speaker()

    def setup_connections(self):
        """Setup signal connections"""
        pass

    def add_speaker(self):
        """Add a new speaker widget"""
        if len(self.speaker_widgets) >= SECTION_LIMITS["max_speakers"]:
            QMessageBox.warning(self, "Limit Reached", f"Maximum {SECTION_LIMITS['max_speakers']} speakers allowed.")
            return

        speaker_widget = SpeakerWidget(self.next_speaker_number)
        speaker_widget.remove_requested.connect(lambda: self.remove_speaker(speaker_widget))

        # Connect data changes
        for widget in [speaker_widget.name_edit, speaker_widget.title_edit,
                      speaker_widget.organization_edit, speaker_widget.contact_edit,
                      speaker_widget.presentation_title_edit]:
            widget.textChanged.connect(lambda: self.data_changed.emit())

        # Insert before stretch
        index = self.speakers_layout.count() - 1
        self.speakers_layout.insertWidget(index, speaker_widget)

        self.speaker_widgets.append(speaker_widget)
        self.next_speaker_number += 1

        self.update_ui_state()
        self.data_changed.emit()

    def remove_speaker(self, speaker_widget):
        """Remove a speaker widget"""
        if len(self.speaker_widgets) <= SECTION_LIMITS["min_speakers"]:
            QMessageBox.warning(self, "Minimum Required", f"At least {SECTION_LIMITS['min_speakers']} speaker is required.")
            return

        self.speaker_widgets.remove(speaker_widget)
        speaker_widget.setParent(None)
        speaker_widget.deleteLater()

        self.update_ui_state()
        self.data_changed.emit()

    def update_ui_state(self):
        """Update UI state based on current speakers"""
        self.add_speaker_button.setEnabled(len(self.speaker_widgets) < SECTION_LIMITS["max_speakers"])

        # Update speaker numbers
        for i, widget in enumerate(self.speaker_widgets, 1):
            widget.speaker_number = i
            widget.findChild(QLabel).setText(f"Speaker {i}")

            # Hide remove button if minimum speakers
            remove_button = widget.findChild(QPushButton, "remove_button")
            if remove_button:
                remove_button.setVisible(len(self.speaker_widgets) > SECTION_LIMITS["min_speakers"])

    def validate_form(self):
        """Validate form inputs"""
        errors = []

        if len(self.speaker_widgets) == 0:
            errors.append("At least one speaker is required")

        for i, speaker_widget in enumerate(self.speaker_widgets, 1):
            if not speaker_widget.is_valid():
                errors.append(f"Speaker {i}: Name is required")

        return errors

    def get_form_data(self):
        """Get form data as dictionary"""
        speakers = []
        for speaker_widget in self.speaker_widgets:
            speakers.append(speaker_widget.get_data())
        return speakers

    def set_form_data(self, speakers_data):
        """Set form data from list of speaker dictionaries"""
        # Clear existing speakers
        for speaker_widget in self.speaker_widgets[:]:
            self.remove_speaker(speaker_widget)

        # Add speakers from data
        for speaker_data in speakers_data:
            if len(self.speaker_widgets) >= SECTION_LIMITS["max_speakers"]:
                break

            self.add_speaker()
            self.speaker_widgets[-1].set_data(speaker_data)

    def save_data(self):
        """Save form data to database"""
        if not self.activity_id:
            QMessageBox.warning(self, "No Activity", "Please save general information first.")
            return False

        try:
            # Validate form
            errors = self.validate_form()
            if errors:
                QMessageBox.warning(self, "Validation Error", "\n".join(errors))
                return False

            # Get speakers data
            speakers_data = self.get_form_data()

            # Save to database
            self.db_service.save_speakers(self.activity_id, speakers_data)

            QMessageBox.information(self, "Success", "Speaker details saved successfully!")
            self.data_changed.emit()
            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
            return False

    def load_data(self):
        """Load form data from database"""
        if not self.activity_id:
            return

        try:
            speakers = self.db_service.get_speakers(self.activity_id)
            if speakers:
                self.set_form_data(speakers)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load data: {str(e)}")

    def set_activity_id(self, activity_id):
        """Set the current activity ID"""
        self.activity_id = activity_id
        if activity_id:
            self.load_data()
        else:
            self.clear_form()

    def clear_form(self):
        """Clear all form fields"""
        # Clear existing speakers
        for speaker_widget in self.speaker_widgets[:]:
            self.remove_speaker(speaker_widget)

        # Add initial empty speaker
        self.add_speaker()