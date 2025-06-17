import yaml
from pathlib import Path

class ResolvedConfig:
    def __init__(self, cli_args:dict, config_dir:Path=Path("config")):
        self.cli_args = cli_args
        self.config = self.load_all_configs(config_dir)

    def load_yaml(self, path):
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def load_all_configs(self, config_dir:Path):
        return {
            "user":self.load_yaml(config_dir/"user.yaml"),
            "backup":self.load_yaml(config_dir/"backup.yaml"),
            "install":self.load_yaml(config_dir/"install.yaml")
        }

    def resolve(self, keys:list, cli_key:str=None, default=None):
        # Priority: CLI > YAML > Default
        cli_val = getattr(self.cli_args, cli_key, None) if cli_key else None
        if cli_val is not None:
            return cli_val

        d = self.config
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return default
        return d

    def __getitem__(self, path):
        keys = path.split(".")
        return self.resolve(keys)