"""
Activity Photos Form
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGroupBox, QScrollArea, QMessageBox,
    QFileDialog, QGridLayout, QApplication, QListWidget,
    QListWidgetItem, QAbstractItemView, QSlider, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QDir, QMimeData
from PyQt5.QtGui import QFont, QPixmap, QPainter, QDragEnterEvent, QDropEvent

from ...utils.constants import FILE_SIZE_LIMITS, SECTION_LIMITS
from ...models.report import ActivityPhoto

class PhotoThumbnail(QWidget):
    """Widget for displaying photo thumbnail"""

    remove_requested = pyqtSignal()

    def __init__(self, photo_path, photo_type="activity", caption=""):
        super().__init__()
        self.photo_path = photo_path
        self.photo_type = photo_type
        self.caption = caption
        self.setMinimumSize(150, 150)
        self.setMaximumSize(200, 220)
        self.setup_ui()

    def setup_ui(self):
        """Setup thumbnail widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Photo preview
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setMinimumSize(140, 140)
        self.photo_label.setMaximumSize(190, 160)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
        """)

        # Load and display photo
        pixmap = QPixmap(self.photo_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                190, 160,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.photo_label.setPixmap(scaled_pixmap)

        layout.addWidget(self.photo_label)

        # Remove button
        self.remove_button = QPushButton("✕")
        self.remove_button.setFixedSize(20, 20)
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.remove_button.clicked.connect(self.remove_requested.emit)

        # Position remove button overlay
        self.remove_button.setParent(self.photo_label)
        self.remove_button.move(self.photo_label.width() - 15, 5)

    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        # Keep remove button in top-right corner
        if hasattr(self, 'remove_button') and hasattr(self, 'photo_label'):
            self.remove_button.move(self.photo_label.width() - 15, 5)

class PhotoUploadArea(QFrame):
    """Drag and drop area for photo upload"""

    photos_uploaded = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setMinimumHeight(200)

    def setup_ui(self):
        """Setup upload area UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)

        self.setAcceptDrops(True)

        # Upload icon and text
        upload_label = QLabel("📷")
        upload_label.setFont(QFont("Arial", 24))
        upload_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(upload_label)

        text_label = QLabel("Drag and drop photos here")
        text_label.setFont(QFont("Arial", 14, QFont.Bold))
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(text_label)

        info_label = QLabel("or click to browse (JPG, PNG - max 5MB each)")
        info_label.setFont(QFont("Arial", 11))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #95a5a6;")
        layout.addWidget(info_label)

        # Browse button
        self.browse_button = QPushButton("Browse Photos")
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.browse_button.clicked.connect(self.browse_photos)
        layout.addWidget(self.browse_button)

        # Set style
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)

    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    border: 2px dashed #3498db;
                    border-radius: 8px;
                    background-color: #e3f2fd;
                }
            """)

    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)

    def dropEvent(self, event):
        """Handle drop event"""
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if self.is_valid_image_file(file_path):
                    files.append(file_path)

        if files:
            self.photos_uploaded.emit(files)

        # Reset style
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)

    def browse_photos(self):
        """Browse for photo files"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Activity Photos",
            QDir.homePath(),
            "Image Files (*.jpg *.jpeg *.png);;All Files (*)"
        )

        valid_files = []
        for file_path in file_paths:
            if self.is_valid_image_file(file_path):
                valid_files.append(file_path)

        if valid_files:
            self.photos_uploaded.emit(valid_files)

    def is_valid_image_file(self, file_path):
        """Check if file is a valid image"""
        if not file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            return False

        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                return False

            # Check file size
            with open(file_path, 'rb') as f:
                file_size = len(f.read())
                if file_size > FILE_SIZE_LIMITS["activity_photo"]:
                    QMessageBox.warning(
                        self, "File Too Large",
                        f"File {file_path.split('/')[-1]} exceeds {FILE_SIZE_LIMITS['activity_photo'] // (1024*1024)}MB limit."
                    )
                    return False

            return True
        except Exception:
            return False

class ActivityPhotosForm(QWidget):
    """Activity Photos form"""

    data_changed = pyqtSignal()

    def __init__(self, db_service, activity_id=None):
        super().__init__()
        self.db_service = db_service
        self.activity_id = activity_id
        self.photos = []  # List of (photo_path, photo_type, caption)
        self.photo_widgets = []

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

        # Form title and status
        header_layout = QHBoxLayout()
        title_label = QLabel("Activity Photos")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title_label)

        self.status_label = QLabel("0 photos uploaded")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()

        form_layout.addLayout(header_layout)

        # Instructions
        instructions = QLabel("Upload activity photos. Minimum 2 photos are required for PDF generation. Maximum 10 photos allowed.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 15px;")
        form_layout.addWidget(instructions)

        # Upload area
        self.upload_area = PhotoUploadArea()
        form_layout.addWidget(self.upload_area)

        # Photos display area
        photos_group = QGroupBox("Uploaded Photos")
        photos_group.setFont(QFont("Arial", 12, QFont.Bold))
        photos_layout = QVBoxLayout(photos_group)

        # Photos container with scroll area
        self.photos_scroll = QScrollArea()
        self.photos_scroll.setWidgetResizable(True)
        self.photos_scroll.setFrameStyle(QFrame.NoFrame)
        self.photos_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: 1px solid #ecf0f1;
                border-radius: 5px;
            }
        """)
        self.photos_scroll.setMinimumHeight(200)

        self.photos_container = QWidget()
        self.photos_layout = QHBoxLayout(self.photos_container)
        self.photos_layout.setSpacing(10)
        self.photos_layout.addStretch()

        self.photos_scroll.setWidget(self.photos_container)
        photos_layout.addWidget(self.photos_scroll)

        form_layout.addWidget(photos_group)

        # Photo type and caption controls
        controls_group = QGroupBox("Photo Settings")
        controls_group.setFont(QFont("Arial", 12, QFont.Bold))
        controls_layout = QGridLayout(controls_group)

        # Photo type selector
        self.photo_type_combo = QComboBox()
        self.photo_type_combo.addItems(["Activity Photo", "Speaker Photo", "Other"])
        controls_layout.addWidget(QLabel("Photo Type:"), 0, 0)
        controls_layout.addWidget(self.photo_type_combo, 0, 1)

        # Caption input
        self.caption_edit = QLineEdit()
        self.caption_edit.setPlaceholderText("Enter photo caption (optional)")
        self.caption_edit.setMaxLength(100)
        controls_layout.addWidget(QLabel("Caption:"), 1, 0)
        controls_layout.addWidget(self.caption_edit, 1, 1)

        form_layout.addWidget(controls_group)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        self.save_button = QPushButton("Save Photos")
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

    def setup_connections(self):
        """Setup signal connections"""
        self.upload_area.photos_uploaded.connect(self.add_photos)

    def add_photos(self, photo_paths):
        """Add photos to the form"""
        for photo_path in photo_paths:
            if len(self.photos) >= SECTION_LIMITS["max_photos"]:
                QMessageBox.warning(
                    self, "Limit Reached",
                    f"Maximum {SECTION_LIMITS['max_photos']} photos allowed."
                )
                break

            # Create photo widget
            photo_type = self.photo_type_combo.currentText().lower().replace(" ", "_")
            caption = self.caption_edit.text().strip()

            photo_widget = PhotoThumbnail(photo_path, photo_type, caption)
            photo_widget.remove_requested.connect(lambda: self.remove_photo(photo_widget))

            # Insert before stretch
            index = self.photos_layout.count() - 1
            self.photos_layout.insertWidget(index, photo_widget)

            # Add to photos list
            self.photos.append((photo_path, photo_type, caption))
            self.photo_widgets.append(photo_widget)

        self.update_status()
        self.data_changed.emit()

    def remove_photo(self, photo_widget):
        """Remove a photo widget"""
        if len(self.photos) <= SECTION_LIMITS["min_photos"]:
            QMessageBox.warning(
                self, "Minimum Required",
                f"At least {SECTION_LIMITS['min_photos']} photos are required."
            )
            return

        if photo_widget in self.photo_widgets:
            index = self.photo_widgets.index(photo_widget)
            del self.photos[index]
            self.photo_widgets.remove(photo_widget)

            photo_widget.setParent(None)
            photo_widget.deleteLater()

        self.update_status()
        self.data_changed.emit()

    def update_status(self):
        """Update status display"""
        count = len(self.photos)
        self.status_label.setText(f"{count} photos uploaded")

        # Change color based on requirements
        if count >= SECTION_LIMITS["min_photos"]:
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.status_label.setStyleSheet(f"color: #e67e22; font-weight: bold;")

    def validate_form(self):
        """Validate form inputs"""
        errors = []

        if len(self.photos) < SECTION_LIMITS["min_photos"]:
            errors.append(f"At least {SECTION_LIMITS['min_photos']} photos are required for PDF generation")

        return errors

    def get_form_data(self):
        """Get form data as dictionary"""
        photos_data = []
        for photo_path, photo_type, caption in self.photos:
            photos_data.append({
                'photo_path': photo_path,
                'photo_type': photo_type,
                'caption': caption
            })
        return photos_data

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

            # Get photos data
            photos_data = self.get_form_data()

            # Save to database
            self.db_service.save_activity_photos(self.activity_id, photos_data)

            QMessageBox.information(self, "Success", "Activity photos saved successfully!")
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
            photos = self.db_service.get_activity_photos(self.activity_id)
            for photo_data in photos:
                if len(self.photos) >= SECTION_LIMITS["max_photos"]:
                    break

                photo_path = photo_data['photo_path']
                photo_type = photo_data['photo_type']
                caption = photo_data.get('caption', '')

                photo_widget = PhotoThumbnail(photo_path, photo_type, caption)
                photo_widget.remove_requested.connect(lambda: self.remove_photo(photo_widget))

                # Insert before stretch
                index = self.photos_layout.count() - 1
                self.photos_layout.insertWidget(index, photo_widget)

                self.photos.append((photo_path, photo_type, caption))
                self.photo_widgets.append(photo_widget)

            self.update_status()

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
        # Remove all photo widgets
        for photo_widget in self.photo_widgets[:]:
            self.remove_photo(photo_widget)

        self.photos.clear()
        self.photo_widgets.clear()
        self.update_status()