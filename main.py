import sys
import logging

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from core.database import create_db_and_tables

# --- Application Setup ---

def setup_application():
    """
    Performs initial setup for the application, such as
    creating the database and configuring logging.
    """
    # Configure basic logging to console and file
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            # You can add a FileHandler here if you want to log to file
            # from the very start.
        ]
    )

    # Initialize the database
    logging.info("Initializing database...")
    create_db_and_tables()
    logging.info("Database initialized successfully.")


def main():
    """
    The main entry point of the application.
    """
    # Perform initial setup
    setup_application()

    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Start the Qt event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
