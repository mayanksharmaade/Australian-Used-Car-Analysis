from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = PROJECT_ROOT / "config" / "config.yaml"


def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Missing configuration file: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if "database" not in config:
        raise ValueError("Missing 'database' section in config/config.yaml")

    return config


def build_connection_string(database_override=None):
    cfg = load_config()["database"]

    database_name = database_override or cfg["database"]

    parts = [
        f"DRIVER={{{cfg['driver']}}}",
        f"SERVER={cfg['server']}",
        f"DATABASE={database_name}",
    ]

    if cfg.get("trusted_connection", True):
        parts.append("Trusted_Connection=yes")
    else:
        parts.extend([
            f"UID={cfg.get('username', '')}",
            f"PWD={cfg.get('password', '')}",
        ])

    parts.append(
        f"Encrypt={'yes' if cfg.get('encrypt', False) else 'no'}"
    )

    parts.append(
        "TrustServerCertificate="
        + ("yes" if cfg.get("trust_server_certificate", True) else "no")
    )

    return ";".join(parts) + ";"
