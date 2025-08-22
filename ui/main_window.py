import logging
import sys

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QTabWidget,
                               QPlainTextEdit)
from PySide6.QtCore import Slot

from core.engine import TradingEngine
from ui.log_handler import QtLogHandler

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    The main window of the Forex Trading Bot application.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forex Trading Bot MVP")
        self.setGeometry(100, 100, 900, 600)

        # Initialize the trading engine
        self.engine = TradingEngine()

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create the tabbed interface
        self.create_tabs()

        # Setup logging to UI
        self.setup_logging()

    def create_tabs(self):
        """Creates the main tab widget for the UI."""
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Create Live Control Tab
        self.live_control_tab = QWidget()
        self.tabs.addTab(self.live_control_tab, "Live Control")
        self.setup_live_control_tab()

        # Create Logs Tab
        self.logs_tab = QWidget()
        self.tabs.addTab(self.logs_tab, "Logs")
        self.setup_logs_tab()

    def setup_live_control_tab(self):
        """Sets up the widgets and layout for the Live Control tab."""
        layout = QVBoxLayout(self.live_control_tab)

        # --- Controls ---
        controls_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Engine")
        self.start_button.clicked.connect(self.start_engine)
        self.stop_button = QPushButton("Stop Engine")
        self.stop_button.clicked.connect(self.stop_engine)
        self.stop_button.setEnabled(False)

        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)

        # --- Status ---
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Engine Status:")
        self.status_value = QLabel("Stopped")
        self.status_value.setStyleSheet("font-weight: bold; color: red;")

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_value)
        status_layout.addStretch()

        layout.addLayout(controls_layout)
        layout.addLayout(status_layout)
        layout.addStretch()

    def setup_logs_tab(self):
        """Sets up the widgets for the Logs tab."""
        layout = QVBoxLayout(self.logs_tab)
        self.log_viewer = QPlainTextEdit()
        self.log_viewer.setReadOnly(True)
        layout.addWidget(self.log_viewer)

    def setup_logging(self):
        """Configures the logging system to redirect logs to the UI."""
        self.log_handler = QtLogHandler()
        self.log_handler.messageWritten.connect(self.append_log_message)

        # Add the UI handler to the root logger
        logging.getLogger().addHandler(self.log_handler)
        # Set the level for the root logger to capture all messages
        logging.getLogger().setLevel(logging.INFO)

    @Slot(str)
    def append_log_message(self, message: str):
        """Appends a message to the log viewer widget."""
        self.log_viewer.appendPlainText(message.strip())

    @Slot()
    def start_engine(self):
        """Handles the Start Engine button click."""
        log.info("UI: Start button clicked.")
        self.engine.start_engine()
        self.update_status(True)

    @Slot()
    def stop_engine(self):
        """Handles the Stop Engine button click."""
        log.info("UI: Stop button clicked.")
        self.engine.stop_engine()
        self.engine.join() # Wait for the thread to finish
        self.update_status(False)

    def update_status(self, is_running: bool):
        """Updates the UI controls based on the engine's status."""
        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        if is_running:
            self.status_value.setText("Running")
            self.status_value.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.status_value.setText("Stopped")
            self.status_value.setStyleSheet("font-weight: bold; color: red;")

    def closeEvent(self, event):
        """Ensures the engine is stopped gracefully when the window is closed."""
        if self.engine.is_alive():
            log.info("Window closing, stopping engine...")
            self.stop_engine()
        event.accept()


if __name__ == '__main__':
    # This part is for testing the window directly
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
