# utils.py
import re
from dateutil import parser
from datetime import datetime
import pandas as pd

def _clean_timezone_parts(s):
    if not isinstance(s, str):
        return s
    text = s.strip()
    # Remove parentheses with timezone tokens
    text = re.sub(r'\(\s*[A-Za-z]{2,6}\s*\)', '', text)
    # Normalize GMT/UTC offsets like "GMT+5" -> "GMT+05:00"
    text = re.sub(r'\b(GMT|UTC)([+-])(\d{1,2})\b',
                  lambda m: f"{m.group(1)}{m.group(2)}{int(m.group(3)):02d}:00",
                  text, flags=re.IGNORECASE)
    # Remove trailing timezone abbreviations like "PDT"
    text = re.sub(r'\s+[A-Za-z]{2,4}$', '', text)
    text = re.sub(r'\s{2,}', ' ', text).strip()
    return text

def parse_datetime_safe(s):
    """
    Parse a datetime string robustly. Returns datetime or raises ValueError.
    """
    if s is None:
        raise ValueError("Empty date value")
    if isinstance(s, datetime):
        return s
    text = str(s).strip()
    if not text:
        raise ValueError("Empty date string")
    cleaned = _clean_timezone_parts(text)
    try:
        dt = parser.parse(cleaned, fuzzy=True)
        return dt
    except Exception:
        # fallback: strip trailing alpha tokens and retry
        fallback = re.sub(r'[A-Za-z]{2,6}$', '', text).strip()
        dt = parser.parse(fallback, fuzzy=True)
        return dt
