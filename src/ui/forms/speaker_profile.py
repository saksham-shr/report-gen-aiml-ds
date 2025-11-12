"""
Speaker Profile Form
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFrame, QGroupBox, QScrollArea, QMessageBox,
    QFileDialog, QGridLayout, QComboBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QDir
from PyQt5.QtGui import QFont, QPixmap

from ...utils.constants import TEXT_LIMITS, FILE_SIZE_LIMITS
from ...models.speaker import Speaker

class SpeakerProfileWidget(QWidget):
    """Individual speaker profile widget"""

    def __init__(self, speaker_data=None, speaker_number=1):
        super().__init__()
        self.speaker_data = speaker_data or {}
        self.speaker_number = speaker_number
        self.profile_image_path = None

        self.setup_ui()

    def setup_ui(self):
        """Setup speaker profile widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel(f"Speaker Profile - {self.speaker_data.get('name', f'Speaker {self.speaker_number}')}")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Profile image section
        image_group = QGroupBox("Profile Image")
        image_group.setFont(QFont("Arial", 11, QFont.Bold))
        image_layout = QVBoxLayout(image_group)
        image_layout.setSpacing(10)

        # Image info
        info_label = QLabel("Upload speaker profile image (JPG/PNG, max 5MB)")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        image_layout.addWidget(info_label)

        # Image display area
        self.image_preview = QLabel("No image uploaded")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setMinimumSize(200, 250)
        self.image_preview.setMaximumSize(250, 300)
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
                color: #7f8c8d;
                font-size: 12px;
                padding: 20px;
            }
        """)
        image_layout.addWidget(self.image_preview, alignment=Qt.AlignCenter)

        # Image buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.upload_button = QPushButton("Upload Image")
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.upload_button.clicked.connect(self.upload_image)
        buttons_layout.addWidget(self.upload_button)

        self.remove_image_button = QPushButton("Remove Image")
        self.remove_image_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.remove_image_button.clicked.connect(self.remove_image)
        self.remove_image_button.setEnabled(False)
        buttons_layout.addWidget(self.remove_image_button)

        buttons_layout.addStretch()
        image_layout.addLayout(buttons_layout)

        layout.addWidget(image_group)

        # Profile text section
        profile_group = QGroupBox("Profile Information")
        profile_group.setFont(QFont("Arial", 11, QFont.Bold))
        profile_layout = QVBoxLayout(profile_group)
        profile_layout.setSpacing(10)

        # Profile info
        profile_info = QLabel("Professional background, achievements, and expertise of the speaker (max 1000 characters)")
        profile_info.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        profile_layout.addWidget(profile_info)

        # Character counter
        counter_layout = QHBoxLayout()
        counter_layout.addStretch()
        self.char_count_label = QLabel("0/1000")
        self.char_count_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic;")
        counter_layout.addWidget(self.char_count_label)
        profile_layout.addLayout(counter_layout)

        # Profile text area
        self.profile_text_edit = QTextEdit()
        self.profile_text_edit.setMaximumHeight(200)
        self.profile_text_edit.setPlaceholderText("Enter speaker profile information...")
        self.profile_text_edit.textChanged.connect(self.update_char_count)

        self.profile_text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                line-height: 1.4;
                background-color: #fafafa;
            }
            QTextEdit:focus {
                border: 1px solid #3498db;
                background-color: white;
            }
        """)

        profile_layout.addWidget(self.profile_text_edit)
        layout.addWidget(profile_group)

        # Set widget style
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin: 5px;
            }
        """)

        # Load existing data if available
        if self.speaker_data:
            self.load_data()

    def upload_image(self):
        """Upload profile image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Profile Image",
            QDir.homePath(),
            "Image Files (*.jpg *.jpeg *.png);;All Files (*)"
        )

        if file_path:
            try:
                # Validate file size
                with open(file_path, 'rb') as f:
                    file_size = len(f.read())
                    if file_size > FILE_SIZE_LIMITS["speaker_profile"]:
                        QMessageBox.warning(
                            self, "File Too Large",
                            f"Image file size exceeds {FILE_SIZE_LIMITS['speaker_profile'] // (1024*1024)}MB limit."
                        )
                        return

                # Load and validate image
                pixmap = QPixmap(file_path)
                if pixmap.isNull():
                    QMessageBox.warning(self, "Invalid Image", "Please select a valid image file.")
                    return

                # Set image
                self.set_profile_image(file_path)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")

    def set_profile_image(self, image_path):
        """Set profile image"""
        self.profile_image_path = image_path
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale the image to fit
                scaled_pixmap = pixmap.scaled(
                    230, 280,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled_pixmap)
                self.image_preview.setStyleSheet("""
                    QLabel {
                        border: 1px solid #3498db;
                        border-radius: 8px;
                        padding: 5px;
                    }
                """)
                self.remove_image_button.setEnabled(True)
            else:
                self.remove_image()
                self.image_preview.setText("Invalid image")
        else:
            self.remove_image()

    def remove_image(self):
        """Remove profile image"""
        self.profile_image_path = None
        self.image_preview.clear()
        self.image_preview.setText("No image uploaded")
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
                color: #7f8c8d;
                font-size: 12px;
                padding: 20px;
            }
        """)
        self.remove_image_button.setEnabled(False)

    def update_char_count(self):
        """Update character count"""
        text = self.profile_text_edit.toPlainText()
        count = len(text)
        self.char_count_label.setText(f"{count}/1000")

        if count > TEXT_LIMITS["speaker_profile"]:
            self.char_count_label.setStyleSheet("color: #e74c3c;")
            # Truncate if over limit
            self.profile_text_edit.setPlainText(text[:TEXT_LIMITS["speaker_profile"]])
            # Move cursor to end
            cursor = self.profile_text_edit.textCursor()
            cursor.movePosition(cursor.End)
            self.profile_text_edit.setTextCursor(cursor)
        else:
            self.char_count_label.setStyleSheet("color: #7f8c8d;")

    def get_data(self):
        """Get speaker profile data"""
        return {
            'id': self.speaker_data.get('id'),
            'name': self.speaker_data.get('name'),
            'title_position': self.speaker_data.get('title_position'),
            'organization': self.speaker_data.get('organization'),
            'contact_info': self.speaker_data.get('contact_info'),
            'presentation_title': self.speaker_data.get('presentation_title'),
            'profile_image_path': self.profile_image_path,
            'profile_text': self.profile_text_edit.toPlainText().strip() or None
        }

    def load_data(self):
        """Load existing speaker data"""
        if self.speaker_data.get('profile_image_path'):
            self.set_profile_image(self.speaker_data['profile_image_path'])

        if self.speaker_data.get('profile_text'):
            self.profile_text_edit.setPlainText(self.speaker_data['profile_text'])

        self.update_char_count()

class SpeakerProfileForm(QWidget):
    """Speaker Profile form"""

    data_changed = pyqtSignal()

    def __init__(self, db_service, activity_id=None):
        super().__init__()
        self.db_service = db_service
        self.activity_id = activity_id
        self.profile_widgets = []

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
        title_label = QLabel("Speaker Profiles")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        form_layout.addWidget(title_label)

        # Instructions
        instructions = QLabel("Add profile images and professional information for each speaker. This section will be synchronized with speakers from Section 2.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 15px;")
        form_layout.addWidget(instructions)

        # Sync button
        sync_layout = QHBoxLayout()
        sync_layout.addStretch()

        self.sync_button = QPushButton("Sync with Speaker Details")
        self.sync_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.sync_button.clicked.connect(self.sync_speakers)
        sync_layout.addWidget(self.sync_button)
        form_layout.addLayout(sync_layout)

        # Profiles container with scroll area
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

        self.profiles_container = QWidget()
        self.profiles_layout = QVBoxLayout(self.profiles_container)
        self.profiles_layout.setSpacing(15)
        self.profiles_layout.addStretch()

        scroll.setWidget(self.profiles_container)
        form_layout.addWidget(scroll)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        self.save_button = QPushButton("Save Profiles")
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

        # Initial load
        self.sync_speakers()

    def setup_connections(self):
        """Setup signal connections"""
        pass

    def sync_speakers(self):
        """Sync speakers with data from Section 2"""
        if not self.activity_id:
            # Show message that activity needs to be created first
            no_activity_label = QLabel("Please save general information first to sync speakers.")
            no_activity_label.setAlignment(Qt.AlignCenter)
            no_activity_label.setStyleSheet("color: #e74c3c; font-size: 14px; padding: 20px;")
            no_activity_label.setMinimumHeight(100)

            # Clear existing widgets
            for widget in self.profile_widgets:
                widget.setParent(None)
                widget.deleteLater()
            self.profile_widgets.clear()

            self.profiles_layout.insertWidget(0, no_activity_label)
            return

        try:
            # Get speakers from database
            speakers = self.db_service.get_speakers(self.activity_id)

            # Clear existing widgets
            for widget in self.profile_widgets:
                widget.setParent(None)
                widget.deleteLater()
            self.profile_widgets.clear()

            if not speakers:
                # Show no speakers message
                no_speakers_label = QLabel("No speakers found. Please add speakers in Section 2 first.")
                no_speakers_label.setAlignment(Qt.AlignCenter)
                no_speakers_label.setStyleSheet("color: #e67e22; font-size: 14px; padding: 20px;")
                no_speakers_label.setMinimumHeight(100)
                self.profiles_layout.insertWidget(0, no_speakers_label)
                return

            # Create profile widgets for each speaker
            for i, speaker_data in enumerate(speakers, 1):
                profile_widget = SpeakerProfileWidget(dict(speaker_data), i)

                # Connect data changes
                profile_widget.profile_text_edit.textChanged.connect(self.data_changed.emit)

                # Insert before stretch
                index = self.profiles_layout.count() - 1
                self.profiles_layout.insertWidget(index, profile_widget)

                self.profile_widgets.append(profile_widget)

        except Exception as e:
            error_label = QLabel(f"Error loading speakers: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #e74c3c; font-size: 14px; padding: 20px;")
            error_label.setMinimumHeight(100)
            self.profiles_layout.insertWidget(0, error_label)

    def validate_form(self):
        """Validate form inputs"""
        # Speaker profiles are optional, so no validation required
        return []

    def get_form_data(self):
        """Get form data as dictionary"""
        profiles = []
        for profile_widget in self.profile_widgets:
            profiles.append(profile_widget.get_data())
        return profiles

    def save_data(self):
        """Save form data to database"""
        if not self.activity_id:
            QMessageBox.warning(self, "No Activity", "Please save general information first.")
            return False

        try:
            # Get profiles data
            profiles_data = self.get_form_data()

            # Update speaker profiles in database
            for profile_data in profiles_data:
                speaker_id = profile_data.get('id')
                if speaker_id:
                    # Update existing speaker
                    self.db_service.db.execute('''
                        UPDATE speakers SET
                            profile_image_path=?, profile_text=?
                        WHERE id=?
                    ''', (
                        profile_data.get('profile_image_path'),
                        profile_data.get('profile_text'),
                        speaker_id
                    ))

            # Commit changes
            self.db_service.db.commit()

            QMessageBox.information(self, "Success", "Speaker profiles saved successfully!")
            self.data_changed.emit()
            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
            return False

    def load_data(self):
        """Load form data from database"""
        self.sync_speakers()

    def set_activity_id(self, activity_id):
        """Set the current activity ID"""
        self.activity_id = activity_id
        if activity_id:
            self.load_data()
        else:
            self.clear_form()

    def clear_form(self):
        """Clear all form fields"""
        # Clear existing widgets
        for widget in self.profile_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.profile_widgets.clear()

        no_activity_label = QLabel("Please save general information first to sync speakers.")
        no_activity_label.setAlignment(Qt.AlignCenter)
        no_activity_label.setStyleSheet("color: #e74c3c; font-size: 14px; padding: 20px;")
        no_activity_label.setMinimumHeight(100)
        self.profiles_layout.insertWidget(0, no_activity_label)