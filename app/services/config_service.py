import yaml

class ConfigService:

    _config = None
    @classmethod
    def get_config(cls):
        if cls._config is None:
            with open("config.yaml","r") as file:
                cls._config = yaml.safe_load(file)
        return cls._config