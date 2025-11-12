"""
Report Prepared By Form
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QFormLayout, QGroupBox, QScrollArea,
    QMessageBox, QFileDialog, QGridLayout, QSizePolicy, QFile
)
from PyQt5.QtCore import Qt, pyqtSignal, QDir
from PyQt5.QtGui import QFont, QPixmap

from ...utils.constants import TEXT_LIMITS, FILE_SIZE_LIMITS, SECTION_LIMITS
from ...models.report import ReportPreparer

class SignatureWidget(QWidget):
    """Widget for displaying signature preview"""

    def __init__(self):
        super().__init__()
        self.signature_path = None
        self.setup_ui()

    def setup_ui(self):
        """Setup signature widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)

        # Preview label
        self.preview_label = QLabel("No signature uploaded")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(150, 80)
        self.preview_label.setMaximumSize(200, 100)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
                color: #7f8c8d;
                font-size: 11px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.preview_label)

        self.setMinimumSize(160, 90)
        self.setMaximumSize(210, 110)

    def set_signature(self, image_path):
        """Set signature image"""
        self.signature_path = image_path
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale the image to fit
                scaled_pixmap = pixmap.scaled(
                    190, 90,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.setStyleSheet("""
                    QLabel {
                        border: 1px solid #3498db;
                        border-radius: 5px;
                        padding: 5px;
                    }
                """)
            else:
                self.clear_signature()
                self.preview_label.setText("Invalid image")
        else:
            self.clear_signature()

    def clear_signature(self):
        """Clear signature"""
        self.signature_path = None
        self.preview_label.clear()
        self.preview_label.setText("No signature uploaded")
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
                color: #7f8c8d;
                font-size: 11px;
                padding: 10px;
            }
        """)

class ReportPreparerWidget(QWidget):
    """Individual report preparer widget"""

    remove_requested = pyqtSignal()

    def __init__(self, preparer_number=1):
        super().__init__()
        self.preparer_number = preparer_number
        self.setup_ui()

    def setup_ui(self):
        """Setup report preparer widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header with remove button
        header_layout = QHBoxLayout()
        title_label = QLabel(f"Report Preparer {self.preparer_number}")
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

        # Form container
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        form_layout.setSpacing(10)

        # Name (required)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter preparer name")
        self.name_edit.setMaxLength(TEXT_LIMITS["preparer_name"])
        form_layout.addWidget(QLabel("Name *:"), 0, 0)
        form_layout.addWidget(self.name_edit, 0, 1)

        # Designation (required)
        self.designation_edit = QLineEdit()
        self.designation_edit.setPlaceholderText("Enter designation")
        self.designation_edit.setMaxLength(TEXT_LIMITS["preparer_designation"])
        form_layout.addWidget(QLabel("Designation *:"), 1, 0)
        form_layout.addWidget(self.designation_edit, 1, 1)

        # Signature section
        signature_group = QGroupBox("Digital Signature")
        signature_group.setFont(QFont("Arial", 10, QFont.Bold))
        signature_layout = QVBoxLayout(signature_group)
        signature_layout.setSpacing(5)

        # Signature info
        info_label = QLabel("Upload signature image (JPG/PNG, max 2MB)")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        signature_layout.addWidget(info_label)

        # Signature upload area
        upload_layout = QHBoxLayout()
        upload_layout.setSpacing(10)

        # Signature preview
        self.signature_widget = SignatureWidget()
        upload_layout.addWidget(self.signature_widget)

        # Upload buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(5)

        self.upload_button = QPushButton("Upload Signature")
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.upload_button.clicked.connect(self.upload_signature)
        buttons_layout.addWidget(self.upload_button)

        self.remove_signature_button = QPushButton("Remove")
        self.remove_signature_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.remove_signature_button.clicked.connect(self.remove_signature)
        self.remove_signature_button.setEnabled(False)
        buttons_layout.addWidget(self.remove_signature_button)

        buttons_layout.addStretch()
        upload_layout.addLayout(buttons_layout)

        signature_layout.addLayout(upload_layout)
        form_layout.addWidget(signature_group, 2, 0, 1, 2)

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

    def upload_signature(self):
        """Upload signature image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Signature Image",
            QDir.homePath(),
            "Image Files (*.jpg *.jpeg *.png);;All Files (*)"
        )

        if file_path:
            # Validate file size
            try:
                file_size = len(QFile(file_path).readAll())
                if file_size > FILE_SIZE_LIMITS["signature"]:
                    QMessageBox.warning(
                        self, "File Too Large",
                        f"Signature file size exceeds {FILE_SIZE_LIMITS['signature'] // (1024*1024)}MB limit."
                    )
                    return

                # Load and validate image
                pixmap = QPixmap(file_path)
                if pixmap.isNull():
                    QMessageBox.warning(self, "Invalid Image", "Please select a valid image file.")
                    return

                # Set signature
                self.signature_widget.set_signature(file_path)
                self.remove_signature_button.setEnabled(True)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load signature: {str(e)}")

    def remove_signature(self):
        """Remove signature"""
        self.signature_widget.clear_signature()
        self.remove_signature_button.setEnabled(False)

    def get_data(self):
        """Get report preparer data"""
        return {
            'name': self.name_edit.text().strip(),
            'designation': self.designation_edit.text().strip(),
            'signature_image_path': self.signature_widget.signature_path
        }

    def set_data(self, data):
        """Set report preparer data"""
        self.name_edit.setText(data.get('name', ''))
        self.designation_edit.setText(data.get('designation', ''))

        signature_path = data.get('signature_image_path')
        if signature_path:
            self.signature_widget.set_signature(signature_path)
            self.remove_signature_button.setEnabled(True)
        else:
            self.remove_signature()

    def is_valid(self):
        """Check if report preparer data is valid"""
        return bool(
            self.name_edit.text().strip() and
            self.designation_edit.text().strip()
        )

class ReportPreparedByForm(QWidget):
    """Report Prepared By form"""

    data_changed = pyqtSignal()

    def __init__(self, db_service, activity_id=None):
        super().__init__()
        self.db_service = db_service
        self.activity_id = activity_id
        self.preparer_widgets = []
        self.next_preparer_number = 1

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
        title_label = QLabel("Report Prepared By")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        form_layout.addWidget(title_label)

        # Instructions
        instructions = QLabel("Add details for each person who prepared this report. At least one preparer is required.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 15px;")
        form_layout.addWidget(instructions)

        # Add preparer button
        self.add_preparer_button = QPushButton("Add Another Preparer")
        self.add_preparer_button.setStyleSheet("""
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
        self.add_preparer_button.clicked.connect(self.add_preparer)
        form_layout.addWidget(self.add_preparer_button)

        # Preparers container with scroll area
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

        self.preparers_container = QWidget()
        self.preparers_layout = QVBoxLayout(self.preparers_container)
        self.preparers_layout.setSpacing(10)
        self.preparers_layout.addStretch()

        scroll.setWidget(self.preparers_container)
        form_layout.addWidget(scroll)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        self.save_button = QPushButton("Save Report Preparers")
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

        # Add initial preparer
        self.add_preparer()

    def setup_connections(self):
        """Setup signal connections"""
        pass

    def add_preparer(self):
        """Add a new preparer widget"""
        if len(self.preparer_widgets) >= SECTION_LIMITS["max_preparers"]:
            QMessageBox.warning(self, "Limit Reached", f"Maximum {SECTION_LIMITS['max_preparers']} preparers allowed.")
            return

        preparer_widget = ReportPreparerWidget(self.next_preparer_number)
        preparer_widget.remove_requested.connect(lambda: self.remove_preparer(preparer_widget))

        # Connect data changes
        self.connect_preparer_signals(preparer_widget)

        # Insert before stretch
        index = self.preparers_layout.count() - 1
        self.preparers_layout.insertWidget(index, preparer_widget)

        self.preparer_widgets.append(preparer_widget)
        self.next_preparer_number += 1

        self.update_ui_state()
        self.data_changed.emit()

    def connect_preparer_signals(self, preparer_widget):
        """Connect signals for a preparer widget"""
        for widget in [preparer_widget.name_edit, preparer_widget.designation_edit]:
            widget.textChanged.connect(lambda: self.data_changed.emit())

    def remove_preparer(self, preparer_widget):
        """Remove a preparer widget"""
        if len(self.preparer_widgets) <= SECTION_LIMITS["min_preparers"]:
            QMessageBox.warning(self, "Minimum Required", f"At least {SECTION_LIMITS['min_preparers']} preparer is required.")
            return

        self.preparer_widgets.remove(preparer_widget)
        preparer_widget.setParent(None)
        preparer_widget.deleteLater()

        self.update_ui_state()
        self.data_changed.emit()

    def update_ui_state(self):
        """Update UI state based on current preparers"""
        self.add_preparer_button.setEnabled(len(self.preparer_widgets) < SECTION_LIMITS["max_preparers"])

        # Update preparer numbers
        for i, widget in enumerate(self.preparer_widgets, 1):
            widget.preparer_number = i
            widget.findChild(QLabel).setText(f"Report Preparer {i}")

            # Hide remove button if minimum preparers
            remove_button = widget.findChild(QPushButton, "remove_button")
            if remove_button:
                remove_button.setVisible(len(self.preparer_widgets) > SECTION_LIMITS["min_preparers"])

    def validate_form(self):
        """Validate form inputs"""
        errors = []

        if len(self.preparer_widgets) == 0:
            errors.append("At least one report preparer is required")

        for i, preparer_widget in enumerate(self.preparer_widgets, 1):
            if not preparer_widget.is_valid():
                errors.append(f"Report Preparer {i}: Name and designation are required")

        return errors

    def get_form_data(self):
        """Get form data as dictionary"""
        preparers = []
        for preparer_widget in self.preparer_widgets:
            preparers.append(preparer_widget.get_data())
        return preparers

    def set_form_data(self, preparers_data):
        """Set form data from list of preparer dictionaries"""
        # Clear existing preparers
        for preparer_widget in self.preparer_widgets[:]:
            self.remove_preparer(preparer_widget)

        # Add preparers from data
        for preparer_data in preparers_data:
            if len(self.preparer_widgets) >= SECTION_LIMITS["max_preparers"]:
                break

            self.add_preparer()
            self.preparer_widgets[-1].set_data(preparer_data)

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

            # Get preparers data
            preparers_data = self.get_form_data()

            # Save to database
            self.db_service.save_report_preparers(self.activity_id, preparers_data)

            QMessageBox.information(self, "Success", "Report preparers saved successfully!")
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
            preparers = self.db_service.get_report_preparers(self.activity_id)
            if preparers:
                self.set_form_data(preparers)
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
        # Clear existing preparers
        for preparer_widget in self.preparer_widgets[:]:
            self.remove_preparer(preparer_widget)

        # Add initial empty preparer
        self.add_preparer()