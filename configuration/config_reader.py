import yaml
import os


class ConfigReader:
    def __init__(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            "config.yaml"
        )

        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

        self.env = self.config["env"]

    @property
    def base_url(self):
        return self.config[self.env]["base_url"]

    @property
    def username(self):
        return self.config[self.env]["username"]

    @property
    def password(self):
        return self.config[self.env]["password"]

    @property
    def ollama_url(self):
        return self.config[self.env]["ollama"]["url"]

    @property
    def ollama_model(self):
        return self.config[self.env]["ollama"]["model"]