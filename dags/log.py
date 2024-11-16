import logging
import os
from datetime import datetime
import pytz  # For handling timezones
import stat  # For setting file permissions

class TZFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt='%Y-%m-%d %H:%M:%S %Z', tz=None):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.tz = tz

    def formatTime(self, record, datefmt=None):
        # Convert the timestamp to the desired timezone
        dt = datetime.fromtimestamp(record.created, tz=self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.strftime('%Y-%m-%d %H:%M:%S %Z') #dt.isoformat()

def init_log(name='log', log_dir="./tmp", log_file="tiki.log"):
    '''
    Initializes the logger with a new log file every time.

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    '''
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Log all levels from DEBUG and above

    # Remove existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()


    # Create handler to write logs to a new file
    file_handler = logging.FileHandler(f'{log_dir}/{log_file}')
    file_handler.setLevel(logging.DEBUG)

    # Log format
    ho_chi_minh_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    formatter = TZFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', tz=ho_chi_minh_tz)
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)
    os.chmod(f'{log_dir}/{log_file}', stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    return logger
