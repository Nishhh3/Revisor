"""
Validates user-submitted signup form data. No known issues --
this case exists to measure PRISM's false-positive rate.
"""

import re

EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")


def validate_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_PATTERN.match(email.strip()))


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    return True, ""


def validate_signup(email: str, password: str) -> dict:
    errors = []
    if not validate_email(email):
        errors.append("Invalid email format")

    valid_pw, pw_error = validate_password(password)
    if not valid_pw:
        errors.append(pw_error)

    return {"valid": len(errors) == 0, "errors": errors}