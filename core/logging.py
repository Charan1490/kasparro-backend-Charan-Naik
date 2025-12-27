"""Structured logging configuration."""
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

from core.config import get_settings

settings = get_settings()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record."""
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add level name
        log_record['level'] = record.levelname
        
        # Add service name
        log_record['service'] = 'crypto-etl-backend'
        
        # Add module info
        if hasattr(record, 'module'):
            log_record['module'] = record.module


def setup_logging() -> logging.Logger:
    """
    Set up structured logging.
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger('crypto_etl')
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with JSON formatting
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(service)s %(module)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_logging()
