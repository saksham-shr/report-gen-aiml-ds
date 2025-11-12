"""
Synopsis Form
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFrame, QGroupBox, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QTextCharFormat, QColor

from ...utils.constants import TEXT_LIMITS

class CharacterLimitedTextEdit(QTextEdit):
    """Text edit with character counter"""

    def __init__(self, max_chars=None, parent=None):
        super().__init__(parent)
        self.max_chars = max_chars
        self.character_count_label = None
        self.setup_text_edit()

    def setup_text_edit(self):
        """Setup the text edit"""
        self.setAcceptRichText(False)
        self.textChanged.connect(self.update_character_count)

    def set_character_count_label(self, label):
        """Set the character count label"""
        self.character_count_label = label
        self.update_character_count()

    def update_character_count(self):
        """Update character count display"""
        if self.character_count_label:
            text = self.toPlainText()
            count = len(text)
            if self.max_chars:
                self.character_count_label.setText(f"{count}/{self.max_chars}")
                if count > self.max_chars:
                    self.character_count_label.setStyleSheet("color: #e74c3c;")
                else:
                    self.character_count_label.setStyleSheet("color: #7f8c8d;")
            else:
                self.character_count_label.setText(f"{count}")

    def insertPlainText(self, text):
        """Override to enforce character limit"""
        if self.max_chars:
            current_text = self.toPlainText()
            if len(current_text) + len(text) > self.max_chars:
                return
        super().insertPlainText(text)

    def paste(self):
        """Override paste to enforce character limit"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if self.max_chars:
            current_text = self.toPlainText()
            available_space = self.max_chars - len(current_text)
            if available_space > 0:
                text = text[:available_space]
            else:
                return
        super().paste()

class SynopsisForm(QWidget):
    """Synopsis form"""

    data_changed = pyqtSignal()

    def __init__(self, db_service, activity_id=None):
        super().__init__()
        self.db_service = db_service
        self.activity_id = activity_id
        self.activity_data = {}

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
        title_label = QLabel("Synopsis of the Activity")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        form_layout.addWidget(title_label)

        # Instructions
        instructions = QLabel("Provide a comprehensive overview of the activity including highlights, key takeaways, and future plans.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 20px;")
        form_layout.addWidget(instructions)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)

        # Highlights section
        highlights_group = self.create_text_section(
            "Highlights of the Activity",
            "Key achievements, important moments, and notable outcomes of the activity.",
            TEXT_LIMITS["highlights"]
        )
        content_layout.addWidget(highlights_group)

        # Key takeaways section
        takeaways_group = self.create_text_section(
            "Key Takeaways",
            "Main lessons learned, skills acquired, and knowledge gained by participants.",
            TEXT_LIMITS["key_takeaway"]
        )
        content_layout.addWidget(takeaways_group)

        # Summary section
        summary_group = self.create_text_section(
            "Summary of the Activity",
            "Comprehensive description of the activity, its purpose, execution, and outcomes.",
            TEXT_LIMITS["summary"]
        )
        content_layout.addWidget(summary_group)

        # Follow-up plan section
        followup_group = self.create_text_section(
            "Follow-up Plan",
            "Future actions, next steps, and ongoing initiatives resulting from this activity.",
            TEXT_LIMITS["follow_up_plan"]
        )
        content_layout.addWidget(followup_group)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        form_layout.addWidget(scroll)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        self.save_button = QPushButton("Save Synopsis")
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

    def create_text_section(self, title, description, max_chars):
        """Create a text section with label, description, text area, and character counter"""
        group = QGroupBox(title)
        group.setFont(QFont("Arial", 13, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                color: #2c3e50;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-bottom: 5px;")
        layout.addWidget(desc_label)

        # Text area container
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)

        # Text area
        text_edit = CharacterLimitedTextEdit(max_chars)
        text_edit.setMinimumHeight(120)
        text_edit.setMaximumHeight(200)
        text_edit.setPlaceholderText(f"Enter {title.lower()}...")

        # Style the text area
        text_edit.setStyleSheet("""
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

        text_layout.addWidget(text_edit)

        # Character counter
        counter_label = QLabel(f"0/{max_chars}")
        counter_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic;")
        counter_label.setAlignment(Qt.AlignRight)
        text_edit.set_character_count_label(counter_label)
        text_layout.addWidget(counter_label)

        layout.addWidget(text_container)

        # Store references for later access
        setattr(self, f"{self.get_field_name(title)}_edit", text_edit)

        return group

    def get_field_name(self, title):
        """Convert title to field name"""
        name_map = {
            "Highlights of the Activity": "highlights",
            "Key Takeaways": "key_takeaway",
            "Summary of the Activity": "summary",
            "Follow-up Plan": "follow_up_plan"
        }
        return name_map.get(title, title.lower().replace(" ", "_"))

    def setup_connections(self):
        """Setup signal connections"""
        text_edits = [
            self.highlights_edit,
            self.key_takeaway_edit,
            self.summary_edit,
            self.follow_up_plan_edit
        ]

        for text_edit in text_edits:
            text_edit.textChanged.connect(self.data_changed.emit)

    def get_form_data(self):
        """Get form data as dictionary"""
        return {
            'highlights': self.highlights_edit.toPlainText().strip() or None,
            'key_takeaway': self.key_takeaway_edit.toPlainText().strip() or None,
            'summary': self.summary_edit.toPlainText().strip() or None,
            'follow_up_plan': self.follow_up_plan_edit.toPlainText().strip() or None
        }

    def set_form_data(self, data):
        """Set form data from dictionary"""
        self.highlights_edit.setPlainText(data.get('highlights', ''))
        self.key_takeaway_edit.setPlainText(data.get('key_takeaway', ''))
        self.summary_edit.setPlainText(data.get('summary', ''))
        self.follow_up_plan_edit.setPlainText(data.get('follow_up_plan', ''))

    def validate_form(self):
        """Validate form inputs"""
        errors = []

        # Check if at least one field has content
        has_content = any([
            self.highlights_edit.toPlainText().strip(),
            self.key_takeaway_edit.toPlainText().strip(),
            self.summary_edit.toPlainText().strip(),
            self.follow_up_plan_edit.toPlainText().strip()
        ])

        if not has_content:
            errors.append("Please provide at least some synopsis content")

        return errors

    def save_data(self):
        """Save form data to database"""
        if not self.activity_id:
            QMessageBox.warning(self, "No Activity", "Please save general information first.")
            return False

        try:
            # Get form data
            form_data = self.get_form_data()

            # Get existing activity data
            activity = self.db_service.get_activity(self.activity_id)
            if activity:
                activity_data = dict(activity)
                activity_data.update(form_data)
                activity_data['id'] = self.activity_id

                # Save to database
                self.db_service.save_activity(activity_data)

                QMessageBox.information(self, "Success", "Synopsis saved successfully!")
                self.data_changed.emit()
                return True
            else:
                QMessageBox.warning(self, "Error", "Activity not found")
                return False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
            return False

    def load_data(self):
        """Load form data from database"""
        if not self.activity_id:
            return

        try:
            activity = self.db_service.get_activity(self.activity_id)
            if activity:
                self.set_form_data(dict(activity))
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
        self.highlights_edit.clear()
        self.key_takeaway_edit.clear()
        self.summary_edit.clear()
        self.follow_up_plan_edit.clear()