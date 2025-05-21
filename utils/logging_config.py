import logging
import os
from datetime import datetime
import sys

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Set up a logger with the specified configuration.
    
    Args:
        name (str): Logger name
        log_file (str, optional): Log file path
        level (int, optional): Logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(project_root, 'logs')
    
    # Create logs directory if it doesn't exist
    if log_file and not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # If no log file specified, use default based on name
    if not log_file and name:
        log_file = os.path.join(logs_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
