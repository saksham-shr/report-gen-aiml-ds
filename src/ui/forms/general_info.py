"""
General Information Form
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateTimeEdit, QPushButton, QFrame, QFormLayout,
    QGroupBox, QGridLayout, QTextEdit, QDateEdit, QTimeEdit,
    QMessageBox
)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator

from ...utils.constants import (
    ACTIVITY_TYPES, SUB_CATEGORIES, TEXT_LIMITS, VALIDATION_MESSAGES
)
from ...models.activity import Activity

class GeneralInfoForm(QWidget):
    """General Information form"""

    data_changed = pyqtSignal()
    activity_saved = pyqtSignal(int)  # Signal to broadcast when activity is saved with activity_id

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
        title_label = QLabel("General Information")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        form_layout.addWidget(title_label)

        # Main form layout
        form_widget = QWidget()
        self.main_form_layout = QFormLayout(form_widget)
        self.main_form_layout.setSpacing(15)

        # Activity Type
        self.activity_type_combo = self.create_combobox(ACTIVITY_TYPES)
        self.activity_type_combo.setMinimumWidth(300)
        self.main_form_layout.addRow("Type of Activity *:", self.activity_type_combo)

        # Sub Category
        sub_category_layout = QHBoxLayout()
        self.sub_category_combo = self.create_combobox(SUB_CATEGORIES)
        self.sub_category_combo.setMinimumWidth(200)
        self.sub_category_combo.currentTextChanged.connect(self.on_sub_category_changed)
        sub_category_layout.addWidget(self.sub_category_combo)

        # Other sub category text field (initially hidden)
        self.sub_category_other_edit = QLineEdit()
        self.sub_category_other_edit.setPlaceholderText("Specify sub category")
        self.sub_category_other_edit.setMaximumWidth(200)
        self.sub_category_other_edit.setVisible(False)
        sub_category_layout.addWidget(self.sub_category_other_edit)

        sub_category_layout.addStretch()
        self.main_form_layout.addRow("Sub Category:", sub_category_layout)

        # Date and Time section
        datetime_group = QGroupBox("Date and Time")
        datetime_group.setFont(QFont("Arial", 12, QFont.Bold))
        datetime_layout = QGridLayout(datetime_group)
        datetime_layout.setSpacing(10)

        # Start Date
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        datetime_layout.addWidget(QLabel("Start Date *:"), 0, 0)
        datetime_layout.addWidget(self.start_date_edit, 0, 1)

        # End Date
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        datetime_layout.addWidget(QLabel("End Date:"), 0, 2)
        datetime_layout.addWidget(self.end_date_edit, 0, 3)

        # Start Time
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(9, 0))
        datetime_layout.addWidget(QLabel("Start Time:"), 1, 0)
        datetime_layout.addWidget(self.start_time_edit, 1, 1)

        # End Time
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(17, 0))
        datetime_layout.addWidget(QLabel("End Time:"), 1, 2)
        datetime_layout.addWidget(self.end_time_edit, 1, 3)

        self.main_form_layout.addRow(datetime_group)

        # Venue
        self.venue_edit = QLineEdit()
        self.venue_edit.setPlaceholderText("Enter venue location")
        self.venue_edit.setMaxLength(TEXT_LIMITS["venue"])
        self.main_form_layout.addRow("Venue:", self.venue_edit)

        # Collaboration/Sponsor
        self.collaboration_edit = QLineEdit()
        self.collaboration_edit.setPlaceholderText("Enter collaboration/sponsor details (if any)")
        self.main_form_layout.addRow("Collaboration/Sponsor:", self.collaboration_edit)

        form_layout.addWidget(form_widget)

        # Add save button
        save_button = QPushButton("Save Information")
        save_button.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        save_button.clicked.connect(self.save_data)
        form_layout.addWidget(save_button, alignment=Qt.AlignRight)

        main_layout.addWidget(form_container)
        main_layout.addStretch()

    def create_combobox(self, items):
        """Create a combobox with items"""
        combo = QComboBox()
        combo.addItem("-- Select --", "")
        for item in items:
            combo.addItem(item, item)
        return combo

    def setup_connections(self):
        """Setup signal connections"""
        # Connect all input changes to data_changed signal
        self.activity_type_combo.currentTextChanged.connect(lambda: self.data_changed.emit())
        self.sub_category_combo.currentTextChanged.connect(lambda: self.data_changed.emit())
        self.sub_category_other_edit.textChanged.connect(lambda: self.data_changed.emit())
        self.start_date_edit.dateChanged.connect(lambda: self.data_changed.emit())
        self.end_date_edit.dateChanged.connect(lambda: self.data_changed.emit())
        self.start_time_edit.timeChanged.connect(lambda: self.data_changed.emit())
        self.end_time_edit.timeChanged.connect(lambda: self.data_changed.emit())
        self.venue_edit.textChanged.connect(lambda: self.data_changed.emit())
        self.collaboration_edit.textChanged.connect(lambda: self.data_changed.emit())

    def on_sub_category_changed(self, text):
        """Handle sub category change"""
        if text == "Other":
            self.sub_category_other_edit.setVisible(True)
            self.sub_category_other_edit.setFocus()
        else:
            self.sub_category_other_edit.setVisible(False)
            self.sub_category_other_edit.clear()

    def validate_form(self):
        """Validate form inputs"""
        errors = []

        # Check required fields
        if not self.activity_type_combo.currentData():
            errors.append("Activity type is required")

        if not self.start_date_edit.date():
            errors.append("Start date is required")

        # Validate date logic
        if self.end_date_edit.date() and self.start_date_edit.date():
            if self.end_date_edit.date() < self.start_date_edit.date():
                errors.append("End date cannot be before start date")

        # Validate time logic
        if self.start_date_edit.date() == self.end_date_edit.date():
            if self.start_time_edit.time() and self.end_time_edit.time():
                if self.end_time_edit.time() < self.start_time_edit.time():
                    errors.append("End time cannot be before start time on the same day")

        # Check other sub category
        if self.sub_category_combo.currentData() == "Other" and not self.sub_category_other_edit.text().strip():
            errors.append("Please specify the sub category when 'Other' is selected")

        return errors

    def get_form_data(self):
        """Get form data as dictionary"""
        sub_category = self.sub_category_combo.currentData()
        if sub_category == "Other":
            sub_category_other = self.sub_category_other_edit.text().strip()
        else:
            sub_category_other = None

        return {
            'activity_type': self.activity_type_combo.currentData(),
            'sub_category': sub_category,
            'sub_category_other': sub_category_other,
            'start_date': self.start_date_edit.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date_edit.date().toString("yyyy-MM-dd") if self.end_date_edit.date() else None,
            'start_time': self.start_time_edit.time().toString("HH:mm"),
            'end_time': self.end_time_edit.time().toString("HH:mm"),
            'venue': self.venue_edit.text().strip() or None,
            'collaboration_sponsor': self.collaboration_edit.text().strip() or None
        }

    def set_form_data(self, data):
        """Set form data from dictionary"""
        self.activity_type_combo.setCurrentText(data.get('activity_type', ''))

        sub_category = data.get('sub_category')
        self.sub_category_combo.setCurrentText(sub_category or '')

        if sub_category == "Other":
            self.sub_category_other_edit.setText(data.get('sub_category_other', '') or '')

        if data.get('start_date'):
            self.start_date_edit.setDate(QDate.fromString(data['start_date'], "yyyy-MM-dd"))

        if data.get('end_date'):
            self.end_date_edit.setDate(QDate.fromString(data['end_date'], "yyyy-MM-dd"))

        if data.get('start_time'):
            self.start_time_edit.setTime(QTime.fromString(data['start_time'], "HH:mm"))

        if data.get('end_time'):
            self.end_time_edit.setTime(QTime.fromString(data['end_time'], "HH:mm"))

        self.venue_edit.setText(data.get('venue') or '')
        self.collaboration_edit.setText(data.get('collaboration_sponsor') or '')

    def save_data(self):
        """Save form data to database"""
        try:
            # Validate form
            errors = self.validate_form()
            if errors:
                QMessageBox.warning(self, "Validation Error", "\n".join(errors))
                return False

            # Get form data
            form_data = self.get_form_data()
            form_data['id'] = self.activity_id

            # Save to database
            activity_id = self.db_service.save_activity(form_data)

            if not self.activity_id:
                self.activity_id = activity_id

            QMessageBox.information(self, "Success", "General information saved successfully!")
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
        self.activity_type_combo.setCurrentIndex(0)
        self.sub_category_combo.setCurrentIndex(0)
        self.sub_category_other_edit.clear()
        self.start_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDate(QDate.currentDate())
        self.start_time_edit.setTime(QTime(9, 0))
        self.end_time_edit.setTime(QTime(17, 0))
        self.venue_edit.clear()
        self.collaboration_edit.clear()