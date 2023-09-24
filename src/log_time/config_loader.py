import yaml

class ConfigLoader:
    def __init__(self, config_file, overrides):
        self.config_file = config_file
        self.overrides = overrides

    def load_config(self):
        with open(self.config_file, "r") as stream:
            config = yaml.safe_load(stream)
            self.__override_config(config)
            return config

    def __override_config(self, config):
        for override in self.overrides:
            override_path = override.split('=')[0].split(".")
            override_value = override.split('=')[1]

            self.__override_dictionary_value(config, override_path, override_value)

    def __override_dictionary_value(self, dict, path, value):
        if len(path) == 1:
            dict[path[0]] = value
        else:
            self.__override_dictionary_value(dict[path[0]], path[1:], value)