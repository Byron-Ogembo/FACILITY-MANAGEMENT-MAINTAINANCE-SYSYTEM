# app/utils/validators.py - Input validation and sanitization
"""
Input validation and sanitization for user-supplied data.
Prevents XSS and invalid data injection.
"""
import re
import html


def sanitize_string(value, max_length=500):
    """Sanitize string input - escape HTML, trim, limit length."""
    if value is None:
        return ''
    s = str(value).strip()[:max_length]
    return html.escape(s)


def sanitize_int(value, default=0, min_val=None, max_val=None):
    """Safe integer conversion with bounds."""
    try:
        n = int(value)
        if min_val is not None and n < min_val:
            return min_val
        if max_val is not None and n > max_val:
            return max_val
        return n
    except (ValueError, TypeError):
        return default


def sanitize_float(value, default=0.0):
    """Safe float conversion."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def validate_required(value, field_name):
    """Check required field is non-empty."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return False, f"{field_name} is required"
    return True, None
