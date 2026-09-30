from etl.common.text_utils import (
    clean_text,
    normalize_key,
    parse_integer,
    parse_decimal,
    parse_price,
)


def test_clean_text():
    assert clean_text("  Toyota   Motor  ") == "Toyota Motor"
    assert clean_text("N/A") is None


def test_normalize_key():
    assert normalize_key("Mercedes-Benz") == "MERCEDES BENZ"


def test_parse_integer():
    assert parse_integer("45,123 km") == 45123
    assert parse_integer("") is None


def test_parse_decimal():
    assert parse_decimal("7.5 L/100km") == 7.5


def test_parse_price():
    assert parse_price("$35,990") == 35990.0
    assert parse_price("POA") is None
