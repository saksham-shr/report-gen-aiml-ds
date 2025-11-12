"""
Main application window with sidebar navigation
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QFrame, QLabel, QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from .widgets.sidebar import Sidebar
from .forms.general_info import GeneralInfoForm
from .forms.speaker_details import SpeakerDetailsForm
from .forms.participants import ParticipantsForm
from .forms.synopsis import SynopsisForm
from .forms.report_prepared_by import ReportPreparedByForm
from .forms.speaker_profile import SpeakerProfileForm
from .forms.activity_photos import ActivityPhotosForm
from .forms.generate_pdf import GeneratePDFForm
from ..utils.constants import UNIVERSITY_INFO, SIDEBAR_ITEMS

class MainWindow(QMainWindow):
    """Main application window"""

    # Signals
    form_data_changed = pyqtSignal()
    activity_saved = pyqtSignal(int)

    def __init__(self, db_service):
        super().__init__()
        self.db_service = db_service
        self.current_activity_id = None
        self.forms = {}
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # Auto-save every 30 seconds

        self.setup_ui()
        self.setup_connections()
        self.current_form_index = 0

    def setup_ui(self):
        """Setup the main window UI"""
        self.setWindowTitle("Academic Activity Report Generator")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Create sidebar
        self.sidebar = Sidebar(SIDEBAR_ITEMS)
        self.sidebar.setMaximumWidth(250)
        self.sidebar.setMinimumWidth(200)
        splitter.addWidget(self.sidebar)

        # Create content area
        self.content_area = QFrame()
        self.content_area.setFrameStyle(QFrame.NoFrame)
        self.content_area.setStyleSheet("background-color: #f5f5f5;")
        splitter.addWidget(self.content_area)

        # Set initial splitter sizes
        splitter.setSizes([250, 950])

        # Setup content layout
        self.setup_content_area()

        # Setup status bar
        self.setup_status_bar()

    def setup_content_area(self):
        """Setup the content area with forms"""
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(0)

        # Add university header
        self.setup_university_header()

        # Create forms container
        self.forms_container = QWidget()
        self.forms_layout = QVBoxLayout(self.forms_container)
        self.forms_layout.setContentsMargins(0, 20, 0, 0)
        self.content_layout.addWidget(self.forms_container)

        # Initialize all forms
        self.initialize_forms()

        # Show first form by default
        self.show_form(0)

    def setup_university_header(self):
        """Setup the university header"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setAlignment(Qt.AlignCenter)

        # University name
        uni_label = QLabel(UNIVERSITY_INFO["name"])
        uni_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        uni_label.setAlignment(Qt.AlignCenter)
        uni_label.setStyleSheet("color: #2c3e50; margin: 2px;")
        header_layout.addWidget(uni_label)

        # School and department
        school_label = QLabel(UNIVERSITY_INFO["school"])
        school_label.setFont(QFont("Times New Roman", 12, QFont.Bold))
        school_label.setAlignment(Qt.AlignCenter)
        school_label.setStyleSheet("color: #34495e; margin: 1px;")
        header_layout.addWidget(school_label)

        dept_label = QLabel(UNIVERSITY_INFO["department"])
        dept_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        dept_label.setAlignment(Qt.AlignCenter)
        dept_label.setStyleSheet("color: #34495e; margin: 1px;")
        header_layout.addWidget(dept_label)

        self.content_layout.addWidget(header_widget)

    def initialize_forms(self):
        """Initialize all form instances"""
        self.general_form = GeneralInfoForm(self.db_service, self.current_activity_id)
        self.forms = {
            0: self.general_form,
            1: SpeakerDetailsForm(self.db_service, self.current_activity_id),
            2: ParticipantsForm(self.db_service, self.current_activity_id),
            3: SynopsisForm(self.db_service, self.current_activity_id),
            4: ReportPreparedByForm(self.db_service, self.current_activity_id),
            5: SpeakerProfileForm(self.db_service, self.current_activity_id),
            6: ActivityPhotosForm(self.db_service, self.current_activity_id),
            7: GeneratePDFForm(self.db_service, self.current_activity_id)
        }

        # Connect activity_saved signal from general form to broadcast activity_id changes
        self.general_form.activity_saved.connect(self.broadcast_activity_id)

        # Add forms to layout (initially hidden)
        for form in self.forms.values():
            form.setVisible(False)
            self.forms_layout.addWidget(form)

        # Set current form
        self.current_form = self.forms[0]
        self.current_form.setVisible(True)

    def setup_connections(self):
        """Setup signal connections"""
        # Sidebar navigation
        self.sidebar.item_clicked.connect(self.show_form)

        # Form data changes
        for form in self.forms.values():
            form.data_changed.connect(self.on_form_data_changed)

    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add status labels
        self.save_status_label = QLabel("Ready")
        self.status_bar.addWidget(self.save_status_label)

        self.activity_status_label = QLabel("No activity loaded")
        self.status_bar.addPermanentWidget(self.activity_status_label)

    def show_form(self, index):
        """Show a specific form by index"""
        # Hide current form
        if self.current_form:
            self.current_form.setVisible(False)

        # Show new form
        if index in self.forms:
            self.current_form = self.forms[index]
            self.current_form.setVisible(True)
            self.current_form_index = index

        # Update sidebar selection
        self.sidebar.set_selected_item(index)

    def on_form_data_changed(self):
        """Handle form data changes"""
        self.form_data_changed.emit()
        self.update_save_status("Unsaved changes")

    def update_save_status(self, status):
        """Update save status in status bar"""
        self.save_status_label.setText(status)

    def auto_save(self):
        """Auto-save current activity data"""
        if self.current_activity_id:
            try:
                # Save current form data
                current_form = self.current_form
                if hasattr(current_form, 'save_data'):
                    current_form.save_data()

                self.update_save_status("Auto-saved")
            except Exception as e:
                self.update_save_status(f"Auto-save failed: {str(e)}")

    def load_activity(self, activity_id):
        """Load an existing activity"""
        self.current_activity_id = activity_id
        self.activity_status_label.setText(f"Activity ID: {activity_id}")

        # Load data into all forms
        for form in self.forms.values():
            form.set_activity_id(activity_id)
            if hasattr(form, 'load_data'):
                form.load_data()

        self.update_save_status("Activity loaded")

    def create_new_activity(self):
        """Create a new activity"""
        # Reset forms
        for form in self.forms.values():
            form.clear_form()
            form.set_activity_id(None)

        self.current_activity_id = None
        self.activity_status_label.setText("New activity")

        # Show first form
        self.show_form(0)
        self.update_save_status("New activity created")

    def broadcast_activity_id(self, activity_id):
        """Broadcast new activity_id to all forms"""
        self.current_activity_id = activity_id
        self.activity_status_label.setText(f"Activity ID: {activity_id}")

        # Update all forms with the new activity_id
        for form in self.forms.values():
            if hasattr(form, 'set_activity_id'):
                form.set_activity_id(activity_id)

        self.update_save_status(f"Activity {activity_id} created")

    def closeEvent(self, event):
        """Handle window close event"""
        # Check for unsaved changes
        if "Unsaved" in self.save_status_label.text():
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                # Trigger save for all forms
                for form in self.forms.values():
                    if hasattr(form, 'save_data'):
                        form.save_data()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
                return

        event.accept()