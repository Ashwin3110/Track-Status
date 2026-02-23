import os
import yaml
from dataclasses import dataclass
from typing import List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class ProviderConfig:
    name: str
    feed_url: str
    feed_type: str
    poll_interval_seconds: int


def load_providers(config_path: str = None) -> List[ProviderConfig]:
    if config_path is None:
        config_path = os.path.join(BASE_DIR, "config", "providers.yaml")

    try:
        with open(config_path, "r") as f:
            raw = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML config: {e}")

    providers = []
    required_fields = ["name", "feed_url", "feed_type", "poll_interval_seconds"]

    for i, entry in enumerate(raw.get("providers", [])):
        missing = [f for f in required_fields if f not in entry]
        if missing:
            raise ValueError(f"Provider at index {i} is missing fields: {missing}")

        supported_types = ["atom", "rss"]
        if entry["feed_type"] not in supported_types:
            raise ValueError(
                f"Provider '{entry['name']}' has unsupported feed_type '{entry['feed_type']}'. "
                f"Supported types: {supported_types}"
            )

        providers.append(ProviderConfig(
            name=entry["name"],
            feed_url=entry["feed_url"],
            feed_type=entry["feed_type"],
            poll_interval_seconds=entry["poll_interval_seconds"]
        ))

    if not providers:
        raise ValueError("No providers found in config file.")

    print(f"[ConfigLoader] Loaded {len(providers)} provider(s): {[p.name for p in providers]}")
    return providers
