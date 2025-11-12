"""
Main entry point for the Academic Activity Report Generator
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale
from src.ui.main_window import MainWindow
from src.services.database import DatabaseService

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Academic Activity Report Generator")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Christ University")

    # Initialize database
    db_service = DatabaseService()
    db_service.initialize_database()

    # Create and show main window
    main_window = MainWindow(db_service)
    main_window.show()

    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()