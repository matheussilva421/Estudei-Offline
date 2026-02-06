"""
Date/time utilities for consistent parsing across the application.
"""

from datetime import datetime


# Supported date formats in order of preference
DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",  # ISO format (preferred, used in DB)
    "%Y-%m-%d",            # ISO date only
    "%d/%m/%Y %H:%M",      # Brazilian format with time
    "%d/%m/%Y",            # Brazilian date only
]


def parse_datetime(date_string, default=None):
    """
    Parse a date string trying multiple formats.
    
    Args:
        date_string: The date string to parse
        default: Default value if parsing fails (defaults to datetime.now())
    
    Returns:
        datetime object or default value
    """
    if default is None:
        default = datetime.now()
    
    if not date_string:
        return default
    
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_string, fmt)
        except (ValueError, TypeError):
            continue
    
    return default


def format_datetime_display(dt, format_str="%d/%m/%Y %H:%M"):
    """Format a datetime for display."""
    if isinstance(dt, str):
        dt = parse_datetime(dt)
    return dt.strftime(format_str) if dt else ""


def format_datetime_db(dt=None):
    """Format a datetime for database storage (ISO format)."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")
