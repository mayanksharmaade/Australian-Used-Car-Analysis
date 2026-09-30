from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_config_exists():
    path = (
        PROJECT_ROOT
        / "config"
        / "config.yaml"
    )

    assert path.exists()


def test_server_name_is_configured():
    path = (
        PROJECT_ROOT
        / "config"
        / "config.yaml"
    )

    cfg = yaml.safe_load(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        cfg["database"]["server"]
        == r"DESKTOP-NEE3MSU\SQLEXPRESS"
    )


def test_database_name_is_configured():
    path = (
        PROJECT_ROOT
        / "config"
        / "config.yaml"
    )

    cfg = yaml.safe_load(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        cfg["database"]["database"]
        == "AustralianUsedCarAnalytics"
    )
