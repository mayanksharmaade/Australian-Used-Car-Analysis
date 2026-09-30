from __future__ import annotations

import re
from typing import Any

import pandas as pd


NULL_TOKENS = {"", "na", "n/a", "none", "null", "nan", "-"}


def clean_text(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.lower() in NULL_TOKENS:
        return None
    return re.sub(r"\s+", " ", text)


def normalize_key(value: Any) -> str | None:
    text = clean_text(value)
    if text is None:
        return None
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_integer(value: Any) -> int | None:
    text = clean_text(value)
    if text is None:
        return None
    digits = re.sub(r"[^0-9-]", "", text)
    if digits in {"", "-"}:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def parse_decimal(value: Any) -> float | None:
    text = clean_text(value)
    if text is None:
        return None

    # Extract the first numeric token instead of concatenating every digit
    # in a unit-bearing string such as '7.5 L/100km'.
    match = re.search(r"-?\d[\d,]*(?:\.\d+)?", text)

    if not match:
        return None

    numeric_text = match.group(0).replace(",", "")

    try:
        return float(numeric_text)
    except ValueError:
        return None


def parse_price(value: Any) -> float | None:
    text = clean_text(value)
    if text is None:
        return None
    if text.upper() in {"POA", "CALL", "ENQUIRE", "CONTACT"}:
        return None
    return parse_decimal(text)


def parse_fuel_consumption(value: Any) -> float | None:
    return parse_decimal(value)
