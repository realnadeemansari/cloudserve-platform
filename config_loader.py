from pathlib import Path
import yaml

class Config:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with self.config_path.open('r') as file:
            self.data = yaml.safe_load(file) or {}

        self._validate()

    def _validate(self):
        # Add any validation logic here if needed
        if "environment" not in self.data:
            raise ValueError("Missing 'environment' key in configuration.")
        if "env_vars" not in self.data:
            raise ValueError("Missing 'env_vars' key in configuration.")

    @property
    def environment(self):
        return self.data["environment"]

    @property
    def env_vars(self):
        return self.data["env_vars"]

    def get_env(self, key):
        return self.env_vars.get(key)

    def is_enabled(self, category: str, stack: str) -> bool:
        """
        Return True only when both the category and individual stack are enabled
        """
        category_config = self.data.get(category)

        if not category_config:
            return False

        if not category_config.get(True, False):
            return False

        for stack_config in category_config.get("stacks", []):
            if stack_config.get("name") == stack:
                return stack_config.get(True, False)
            
        return False
