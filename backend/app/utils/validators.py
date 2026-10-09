import re
from typing import Optional


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def validate_phone(phone: str) -> bool:
    return bool(PHONE_REGEX.match(phone))


def sanitize_string(value: str, max_length: int = 1000) -> str:
    if not value:
        return ""
    cleaned = " ".join(value.split())
    return cleaned[:max_length]


def validate_role(role: str) -> bool:
    return role in {"player", "coach", "club", "organizer", "referee", "admin"}


def validate_positive_int(value: int, max_value: Optional[int] = None) -> bool:
    if value <= 0:
        return False
    if max_value is not None and value > max_value:
        return False
    return True