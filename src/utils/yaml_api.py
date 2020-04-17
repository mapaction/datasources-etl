import yaml


def parse_config():
    with open("config.yml", 'r') as stream:
        config = yaml.safe_load(stream)
    return config
