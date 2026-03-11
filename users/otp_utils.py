"""
OTP Utilities for Gym Check-in Verification
--------------------------------------------
Generate and validate OTPs for gym owner verification system.
"""
import random
import string


def generate_otp(length: int = 6) -> str:
    """
    Generate a random numeric OTP.
    
    Args:
        length: Length of OTP (default: 6 digits)
    
    Returns:
        String containing random digits
    """
    return ''.join(random.choices(string.digits, k=length))


def validate_otp(entered_otp: str, stored_otp: str) -> bool:
    """
    Validate entered OTP against stored OTP.
    
    Args:
        entered_otp: OTP entered by gym owner
        stored_otp: OTP stored in booking
    
    Returns:
        True if OTPs match, False otherwise
    """
    if not entered_otp or not stored_otp:
        return False
    
    # Strip whitespace and compare
    return entered_otp.strip() == stored_otp.strip()
