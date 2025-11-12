"""
Participants Profile Form
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QPushButton, QFrame, QFormLayout, QGroupBox,
    QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ...utils.constants import PARTICIPANT_TYPES, SECTION_LIMITS

class ParticipantWidget(QWidget):
    """Individual participant type widget"""

    remove_requested = pyqtSignal()

    def __init__(self, participant_number=1, used_types=None):
        super().__init__()
        self.participant_number = participant_number
        self.used_types = used_types or []
        self.setup_ui()

    def setup_ui(self):
        """Setup participant widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header with remove button
        header_layout = QHBoxLayout()
        title_label = QLabel(f"Participant Type {self.participant_number}")
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

        # Participant form
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(8)

        # Type selection
        self.type_combo = QComboBox()
        self.populate_participant_types()
        form_layout.addRow("Type of Participants *:", self.type_combo)

        # Number of participants
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setMinimum(1)
        self.count_spinbox.setMaximum(9999)
        self.count_spinbox.setValue(1)
        form_layout.addRow("Number of Participants *:", self.count_spinbox)

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

    def populate_participant_types(self):
        """Populate participant type dropdown excluding used types"""
        self.type_combo.clear()
        self.type_combo.addItem("-- Select --", "")

        for type_value, display_name in PARTICIPANT_TYPES:
            if type_value not in self.used_types:
                self.type_combo.addItem(display_name, type_value)

    def update_used_types(self, used_types):
        """Update used types and refresh dropdown"""
        self.used_types = used_types
        current_data = self.type_combo.currentData()
        self.populate_participant_types()
        # Restore current selection if still available
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == current_data:
                self.type_combo.setCurrentIndex(i)
                break

    def get_data(self):
        """Get participant data"""
        return {
            'participant_type': self.type_combo.currentData(),
            'count': self.count_spinbox.value()
        }

    def set_data(self, data):
        """Set participant data"""
        participant_type = data.get('participant_type')
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == participant_type:
                self.type_combo.setCurrentIndex(i)
                break

        self.count_spinbox.setValue(data.get('count', 1))

    def is_valid(self):
        """Check if participant data is valid"""
        return bool(self.type_combo.currentData() and self.count_spinbox.value() > 0)

class ParticipantsForm(QWidget):
    """Participants Profile form"""

    data_changed = pyqtSignal()

    def __init__(self, db_service, activity_id=None):
        super().__init__()
        self.db_service = db_service
        self.activity_id = activity_id
        self.participant_widgets = []
        self.next_participant_number = 1

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
        title_label = QLabel("Participants Profile")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        form_layout.addWidget(title_label)

        # Instructions
        instructions = QLabel("Add participant types for the activity. Each type can only be used once.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 15px;")
        form_layout.addWidget(instructions)

        # Total participants display
        self.total_label = QLabel("Total Participants: 0")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_label.setStyleSheet("color: #27ae60; margin-bottom: 15px;")
        form_layout.addWidget(self.total_label)

        # Add participant button
        self.add_participant_button = QPushButton("Add Participant Type")
        self.add_participant_button.setStyleSheet("""
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
        self.add_participant_button.clicked.connect(self.add_participant)
        form_layout.addWidget(self.add_participant_button)

        # Participants container with scroll area
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

        self.participants_container = QWidget()
        self.participants_layout = QVBoxLayout(self.participants_container)
        self.participants_layout.setSpacing(10)
        self.participants_layout.addStretch()

        scroll.setWidget(self.participants_container)
        form_layout.addWidget(scroll)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        self.save_button = QPushButton("Save Participants")
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

        # Add initial participant
        self.add_participant()

    def setup_connections(self):
        """Setup signal connections"""
        pass

    def get_used_types(self):
        """Get list of currently used participant types"""
        used_types = []
        for widget in self.participant_widgets:
            participant_type = widget.get_data().get('participant_type')
            if participant_type:
                used_types.append(participant_type)
        return used_types

    def add_participant(self):
        """Add a new participant widget"""
        if len(self.participant_widgets) >= SECTION_LIMITS["max_participants"]:
            QMessageBox.warning(self, "Limit Reached", f"Maximum {SECTION_LIMITS['max_participants']} participant types allowed.")
            return

        used_types = self.get_used_types()
        participant_widget = ParticipantWidget(self.next_participant_number, used_types)
        participant_widget.remove_requested.connect(lambda: self.remove_participant(participant_widget))

        # Connect data changes
        participant_widget.type_combo.currentTextChanged.connect(self.update_participant_types)
        participant_widget.count_spinbox.valueChanged.connect(self.update_total)

        # Insert before stretch
        index = self.participants_layout.count() - 1
        self.participants_layout.insertWidget(index, participant_widget)

        self.participant_widgets.append(participant_widget)
        self.next_participant_number += 1

        self.update_ui_state()
        self.update_total()
        self.data_changed.emit()

    def remove_participant(self, participant_widget):
        """Remove a participant widget"""
        if len(self.participant_widgets) <= SECTION_LIMITS["min_participants"]:
            QMessageBox.warning(self, "Minimum Required", f"At least {SECTION_LIMITS['min_participants']} participant type is required.")
            return

        self.participant_widgets.remove(participant_widget)
        participant_widget.setParent(None)
        participant_widget.deleteLater()

        self.update_participant_types()
        self.update_ui_state()
        self.update_total()
        self.data_changed.emit()

    def update_participant_types(self):
        """Update participant type dropdowns"""
        used_types = self.get_used_types()
        for widget in self.participant_widgets:
            widget.update_used_types(used_types)

    def update_total(self):
        """Update total participants count"""
        total = sum(widget.get_data().get('count', 0) for widget in self.participant_widgets)
        self.total_label.setText(f"Total Participants: {total}")

    def update_ui_state(self):
        """Update UI state based on current participants"""
        self.add_participant_button.setEnabled(
            len(self.participant_widgets) < SECTION_LIMITS["max_participants"] and
            len(self.get_used_types()) < len(PARTICIPANT_TYPES)
        )

        # Update participant numbers
        for i, widget in enumerate(self.participant_widgets, 1):
            widget.participant_number = i
            widget.findChild(QLabel).setText(f"Participant Type {i}")

            # Hide remove button if minimum participants
            remove_button = widget.findChild(QPushButton, "remove_button")
            if remove_button:
                remove_button.setVisible(len(self.participant_widgets) > SECTION_LIMITS["min_participants"])

    def validate_form(self):
        """Validate form inputs"""
        errors = []

        if len(self.participant_widgets) == 0:
            errors.append("At least one participant type is required")

        for i, participant_widget in enumerate(self.participant_widgets, 1):
            if not participant_widget.is_valid():
                errors.append(f"Participant Type {i}: Both type and count are required")

        return errors

    def get_form_data(self):
        """Get form data as dictionary"""
        participants = []
        for participant_widget in self.participant_widgets:
            participants.append(participant_widget.get_data())
        return participants

    def set_form_data(self, participants_data):
        """Set form data from list of participant dictionaries"""
        # Clear existing participants
        for participant_widget in self.participant_widgets[:]:
            self.remove_participant(participant_widget)

        # Add participants from data
        for participant_data in participants_data:
            if len(self.participant_widgets) >= SECTION_LIMITS["max_participants"]:
                break

            self.add_participant()
            self.participant_widgets[-1].set_data(participant_data)

        self.update_total()

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

            # Get participants data
            participants_data = self.get_form_data()

            # Save to database
            self.db_service.save_participants(self.activity_id, participants_data)

            QMessageBox.information(self, "Success", "Participants saved successfully!")
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
            participants = self.db_service.get_participants(self.activity_id)
            if participants:
                self.set_form_data(participants)
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
        # Clear existing participants
        for participant_widget in self.participant_widgets[:]:
            self.remove_participant(participant_widget)

        # Add initial empty participant
        self.add_participant()
        self.update_total()