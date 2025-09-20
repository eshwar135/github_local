# services/prompt_service.py
import re

# Service-level defaults and limits
DEFAULT_MAX_TOKENS = 256
MAX_ALLOWED_TOKENS = 1024
MAX_PROMPT_LENGTH = 5000  # characters
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 1.0

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

class ValidationError(ValueError):
    pass

def sanitize_prompt(prompt: str) -> str:
    """Basic sanitization: trim and remove control chars."""
    if not isinstance(prompt, str):
        raise ValidationError("prompt must be a string")
    s = prompt.strip()
    s = CONTROL_CHARS.sub("", s)
    return s

def validate_and_prepare(prompt: str, max_tokens=None, temperature=None):
    """
    Validate and return a dict with sanitized prompt, max_tokens (int), temperature (float).
    Raises ValidationError on invalid input.
    """
    if prompt is None or (isinstance(prompt, str) and prompt.strip() == ""):
        raise ValidationError("prompt is required")

    s_prompt = sanitize_prompt(prompt)

    if len(s_prompt) > MAX_PROMPT_LENGTH:
        raise ValidationError(f"prompt too long (max {MAX_PROMPT_LENGTH} chars)")

    # Validate max_tokens
    try:
        if max_tokens is None:
            max_tokens = DEFAULT_MAX_TOKENS
        else:
            max_tokens = int(max_tokens)
    except Exception:
        raise ValidationError("max_tokens must be an integer")

    if max_tokens < 1:
        raise ValidationError("max_tokens must be >= 1")
    if max_tokens > MAX_ALLOWED_TOKENS:
        max_tokens = MAX_ALLOWED_TOKENS  # clamp

    # Validate temperature
    try:
        if temperature is None:
            temperature = 0.0
        else:
            temperature = float(temperature)
    except Exception:
        raise ValidationError("temperature must be a number")

    if temperature < MIN_TEMPERATURE:
        temperature = MIN_TEMPERATURE
    if temperature > MAX_TEMPERATURE:
        temperature = MAX_TEMPERATURE

    return {
        "prompt": s_prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
