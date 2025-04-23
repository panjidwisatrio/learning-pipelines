import logging
import os
import sys
from datetime import datetime
from config import logging_config, paths_config

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors to console logs
    """
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[91m\033[1m',  # Bold Red
        'RESET': '\033[0m'    # Reset
    }

    def format(self, record):
        log_message = super().format(record)
        if record.levelname in self.COLORS:
            return f"{self.COLORS[record.levelname]}{log_message}{self.COLORS['RESET']}"
        return log_message

def setup_logger(name="linkedin_learning_pipeline"):
    """
    Set up and configure logger based on config settings
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Get log level from config
    log_level_str = logging_config.get("level", "info").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)
    
    # Clear existing handlers (to avoid duplication)
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatters
    simple_format = "%(asctime)s [%(levelname)s] %(message)s"
    detailed_format = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
    
    file_formatter = logging.Formatter(detailed_format, datefmt="%Y-%m-%d %H:%M:%S")
    console_formatter = ColoredFormatter(simple_format, datefmt="%H:%M:%S")
    
    # Add file handler if enabled
    if logging_config.get("log_to_file", True):
        # Create logs directory if it doesn't exist
        log_dir = paths_config.get("log_dir", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(log_dir, f"pipeline-{timestamp}.log")
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Add console handler if enabled
    if logging_config.get("log_to_console", True):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger

# Create a default logger instance
logger = setup_logger()

def get_logger(name=None):
    """
    Get a logger instance. If name is provided, return a child logger.
    """
    if name:
        return logging.getLogger(f"linkedin_learning_pipeline.{name}")
    return logger