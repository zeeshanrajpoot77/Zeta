import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- Type Hinting ---
# For clarity, though we use a dynamic object for attribute access.
AccountConfig = Dict[str, Any]
RiskManagementConfig = Dict[str, Any]
StrategyLabConfig = Dict[str, Any]
AppSettingsConfig = Dict[str, Any]
UIConfig = Dict[str, Any]


class _DataObject:
    """A helper class to convert nested dictionaries to objects for attribute access."""
    def __init__(self, data: Dict[str, Any]):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, _DataObject(value))
            elif isinstance(value, list):
                setattr(self, key, [_DataObject(i) if isinstance(i, dict) else i for i in value])
            else:
                setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.__dict__}>"


class Config:
    """
    A singleton class to manage application configuration.

    It loads settings from a `config.yaml` file and provides them as
    easily accessible attributes. This ensures that configuration is loaded
    only once and is available globally.

    Usage:
        config = Config()
        api_key = config.app_settings.api_key
        accounts = config.accounts
    """
    _instance: Optional['Config'] = None

    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path: str = "config.yaml"):
        if self._initialized:
            return

        self.config_path = Path(config_path)
        self._data: Optional[_DataObject] = None
        self.load_config()

        self._initialized = True

    def load_config(self):
        """Loads the configuration from the YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at: {self.config_path.resolve()}")

        with open(self.config_path, 'r') as f:
            raw_config = yaml.safe_load(f)

        if not raw_config:
            raise ValueError("Configuration file is empty or invalid.")

        self._data = _DataObject(raw_config)

    def reload(self):
        """Reloads the configuration from the file."""
        self.load_config()

    def __getattr__(self, name: str) -> Any:
        """Provides attribute-style access to the configuration data."""
        if self._data and hasattr(self._data, name):
            return getattr(self._data, name)
        raise AttributeError(f"'Config' object has no attribute '{name}'")

    @property
    def accounts(self) -> List[AccountConfig]:
        return self.__getattr__('accounts')

    @property
    def risk_management(self) -> RiskManagementConfig:
        return self.__getattr__('risk_management')

    @property
    def strategy_lab(self) -> StrategyLabConfig:
        return self.__getattr__('strategy_lab')

    @property
    def app_settings(self) -> AppSettingsConfig:
        return self.__getattr__('app_settings')

    @property
    def ui(self) -> UIConfig:
        return self.__getattr__('ui')


# Global instance for easy access across the application
config = Config()
