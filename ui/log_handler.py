import logging
from PySide6.QtCore import QObject, Signal


class QtLogHandler(logging.Handler, QObject):
    """
    A custom logging handler that emits a Qt signal for each log record.

    This allows log messages from any thread to be safely displayed in a
    Qt widget (like a QTextEdit) by connecting its `messageWritten` signal
    to a slot in the main UI thread.
    """
    # Define a new signal that will carry the log message string.
    messageWritten = Signal(str)

    def __init__(self):
        # Initialize both parent classes
        logging.Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record: logging.LogRecord):
        """
        Formats the log record and emits the messageWritten signal.

        This method is called by the logging framework for each log message.
        """
        try:
            msg = self.format(record)
            # Emit the signal with the formatted message
            self.messageWritten.emit(msg)
        except Exception:
            self.handleError(record)
