"""Configuration management for GMB fantasy football dashboard."""
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import keyring
import yaml

# Update config location to be relative to the package
CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
KEYRING_SERVICE = "gmb-fantasy"


@dataclass
class DashboardConfig:
    """Configuration settings for fantasy football dashboard."""

    league_id: int
    year: int
    espn_s2: str | None = None
    swid: str | None = None

    @classmethod
    def load(cls) -> "DashboardConfig":
        """
        Load configuration from various sources in order of precedence:
        1. Environment variables
        2. YAML config file
        3. System keyring (for credentials)
        """
        # Try environment variables first
        config_dict = cls._load_from_env()
        if all(config_dict.values()):
            return cls(**config_dict)

        # Try YAML config file
        yaml_config = cls._load_from_yaml()
        if yaml_config:
            config_dict.update({k: v for k, v in yaml_config.items() if v is not None})

        # Try keyring for credentials
        keyring_config = cls._load_from_keyring()
        if keyring_config:
            config_dict.update({k: v for k, v in keyring_config.items() if v is not None})

        if not config_dict.get("league_id"):
            raise ValueError("League ID must be set in environment, config file, or keyring")

        return cls(**config_dict)

    @staticmethod
    def _load_from_env() -> dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            "league_id": int(os.getenv("GMB_LEAGUE_ID", "0")),
            "year": int(os.getenv("GMB_YEAR", "2024")),
            "espn_s2": os.getenv("GMB_ESPN_S2"),
            "swid": os.getenv("GMB_SWID"),
        }

    @staticmethod
    def _load_from_yaml() -> dict[str, Any] | None:
        """Load configuration from YAML file.

        Returns:
            Configuration dictionary or None if file doesn't exist or is invalid
        """
        if not CONFIG_FILE.exists():
            return None

        try:
            with open(CONFIG_FILE) as f:
                config: dict[str, Any] | None = yaml.safe_load(f)
                if config:
                    config["league_id"] = int(config["league_id"])
                    config["year"] = int(config["year"])
                    return config
                return None
        except (yaml.YAMLError, KeyError, ValueError):
            return None

    @staticmethod
    def _load_from_keyring() -> dict[str, Any]:
        """Load credentials from system keyring."""
        return {
            "espn_s2": keyring.get_password(KEYRING_SERVICE, "espn_s2"),
            "swid": keyring.get_password(KEYRING_SERVICE, "swid"),
        }

    def save(self) -> None:
        """
        Save configuration to YAML file and credentials to keyring.
        """
        # Ensure config directory exists
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Save non-sensitive config to YAML
        yaml_config = {
            "league_id": self.league_id,
            "year": self.year,
        }
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(yaml_config, f)

        # Save credentials to keyring if they exist
        if self.espn_s2:
            keyring.set_password(KEYRING_SERVICE, "espn_s2", self.espn_s2)
        if self.swid:
            keyring.set_password(KEYRING_SERVICE, "swid", self.swid)

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)