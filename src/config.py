import yaml
import os
from typing import Dict, Any

DEFAULT_CONFIG = {
    "web": {
        "favor_recall": True,
        "include_comments": False,
        "include_tables": True
    },
    "wiki": {
        "user_agent": "WebCatcher/1.0 (https://github.com/uttam/web_catcher)",
        "language": "en"
    },
    "pdf": {
        "extract_images": True,
        "detect_tables": True
    }
}

class Config:
    def __init__(self, config_path: str = None):
        self.settings = DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self._update_recursive(self.settings, user_config)

    def _update_recursive(self, base: Dict[Any, Any], update: Dict[Any, Any]):
        for k, v in update.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                self._update_recursive(base[k], v)
            else:
                base[k] = v

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        val = self.settings
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val
