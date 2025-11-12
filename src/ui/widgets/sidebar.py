"""
Sidebar navigation widget
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
    QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QCursor

class SidebarButton(QLabel):
    """Custom sidebar button"""

    clicked = pyqtSignal(int)

    def __init__(self, index, icon, text):
        super().__init__()
        self.index = index
        self.icon = icon
        self.text = text

        self.setup_ui()
        self.setup_style()

    def setup_ui(self):
        """Setup button UI"""
        self.setText(f"{self.icon}  {self.text}")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def setup_style(self):
        """Setup button style"""
        self.setStyleSheet("""
            QLabel {
                padding: 12px 20px;
                margin: 2px 8px;
                border-radius: 8px;
                background-color: transparent;
                color: #2c3e50;
                font-size: 13px;
                font-weight: 500;
            }
            QLabel:hover {
                background-color: #e8f4f8;
                color: #2980b9;
            }
        """)

    def set_selected(self, selected):
        """Set selected state"""
        if selected:
            self.setStyleSheet("""
                QLabel {
                    padding: 12px 20px;
                    margin: 2px 8px;
                    border-radius: 8px;
                    background-color: #3498db;
                    color: white;
                    font-size: 13px;
                    font-weight: 600;
                }
            """)
        else:
            self.setup_style()

    def mousePressEvent(self, event):
        """Handle mouse press"""
        self.clicked.emit(self.index)

class Sidebar(QWidget):
    """Sidebar navigation widget"""

    item_clicked = pyqtSignal(int)

    def __init__(self, items):
        super().__init__()
        self.items = items
        self.buttons = []
        self.setup_ui()
        self.setup_style()

    def setup_ui(self):
        """Setup sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(0)

        # Title
        title = QLabel("Navigation")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #2c3e50;
            padding: 10px;
            margin-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        """)
        layout.addWidget(title)

        # Scroll area for navigation items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc3c7;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95a5a6;
            }
        """)

        # Buttons container
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(0)

        # Create navigation buttons
        for index, (icon, text) in enumerate(self.items):
            button = SidebarButton(index, icon, text)
            button.clicked.connect(self.on_item_clicked)
            buttons_layout.addWidget(button)
            self.buttons.append(button)

        # Add stretch at bottom
        buttons_layout.addStretch()

        scroll.setWidget(buttons_widget)
        layout.addWidget(scroll)

    def setup_style(self):
        """Setup sidebar style"""
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-right: 1px solid #ecf0f1;
            }
        """)

    def on_item_clicked(self, index):
        """Handle item click"""
        self.set_selected_item(index)
        self.item_clicked.emit(index)

    def set_selected_item(self, index):
        """Set selected item"""
        for i, button in enumerate(self.buttons):
            button.set_selected(i == index)