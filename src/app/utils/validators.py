import re
from functools import wraps
from flask import request, session, abort
import time

# Email validation regex - RFC 5322 compliant simplified version
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

# Disposable email domain blocklist (common spam domains)
DISPOSABLE_EMAIL_DOMAINS = {
    'tempmail.com', 'throwaway.email', 'guerrillamail.com', 'mailinator.com',
    'temp-mail.org', '10minutemail.com', 'fakeinbox.com', 'trashmail.com',
    'getnada.com', 'maildrop.cc', 'dispostable.com', 'yopmail.com',
    'sharklasers.com', 'spam4.me', 'grr.la', 'guerrillamail.info',
    'pokemail.net', 'spam.la', 'emailondeck.com', 'tempail.com'
}

# Rate limiting storage (in production, use Redis)
_rate_limit_store = {}


def is_valid_email(email: str) -> tuple[bool, str]:
    """
    Validate email address format and check against disposable domains.
    Returns (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    email = email.strip().lower()
    
    # Check length
    if len(email) > 254:
        return False, "Email is too long"
    
    if len(email) < 5:
        return False, "Email is too short"
    
    # Check format
    if not EMAIL_REGEX.match(email):
        return False, "Invalid email format"
    
    # Extract domain
    try:
        domain = email.split('@')[1]
    except IndexError:
        return False, "Invalid email format"
    
    # Check against disposable email domains
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        return False, "Disposable email addresses are not allowed"
    
    return True, ""


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize a string input by stripping whitespace and limiting length.
    """
    if not value:
        return ""
    
    # Strip whitespace and limit length
    value = str(value).strip()[:max_length]
    
    # Remove null bytes and other dangerous characters
    value = value.replace('\x00', '').replace('\r', '')
    
    return value


def is_valid_name(name: str) -> tuple[bool, str]:
    """
    Validate a name field.
    Returns (is_valid, error_message)
    """
    if not name:
        return False, "Name is required"
    
    name = name.strip()
    
    if len(name) < 1:
        return False, "Name is too short"
    
    if len(name) > 100:
        return False, "Name is too long (max 100 characters)"
    
    # Check for suspicious patterns (SQL injection attempts, scripts)
    suspicious_patterns = [
        '<script', 'javascript:', 'onclick', 'onerror',
        '--', '/*', '*/', 'xp_', 'sp_', 'exec(', 'execute('
    ]
    
    name_lower = name.lower()
    for pattern in suspicious_patterns:
        if pattern in name_lower:
            return False, "Invalid characters in name"
    
    return True, ""


def is_valid_message(message: str) -> tuple[bool, str]:
    """
    Validate a message field.
    Returns (is_valid, error_message)
    """
    if not message:
        return True, ""  # Message is optional
    
    message = message.strip()
    
    if len(message) > 500:
        return False, "Message is too long (max 500 characters)"
    
    # Check for suspicious patterns
    suspicious_patterns = [
        '<script', 'javascript:', 'onclick', 'onerror'
    ]
    
    message_lower = message.lower()
    for pattern in suspicious_patterns:
        if pattern in message_lower:
            return False, "Invalid content in message"
    
    return True, ""


def is_valid_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    # Check for at least one letter and one number
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not has_letter or not has_digit:
        return False, "Password must contain at least one letter and one number"
    
    return True, ""


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """
    Rate limiting decorator.
    Limits requests per user session or IP address.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get identifier (user_id or IP)
            identifier = session.get('user_id') or request.remote_addr
            key = f"{f.__name__}:{identifier}"
            
            current_time = time.time()
            
            # Clean old entries
            if key in _rate_limit_store:
                _rate_limit_store[key] = [
                    t for t in _rate_limit_store[key]
                    if current_time - t < window_seconds
                ]
            else:
                _rate_limit_store[key] = []
            
            # Check rate limit
            if len(_rate_limit_store[key]) >= max_requests:
                abort(429)  # Too Many Requests
            
            # Add current request
            _rate_limit_store[key].append(current_time)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator
