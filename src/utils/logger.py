# src/utils/logger.py

import logging
import os

# Define the directory for logs
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Create and configure the logger
def setup_logging():
    logger = logging.getLogger('application_logger')
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs

    # Define a log format
    formatter = logging.Formatter(format='%(asctime)s - %(levelname)s - %(message)s')

    
    #logger.addHandler(console_handler)
    
    return logger

# Get the configured logger instance
logger = setup_logging()
