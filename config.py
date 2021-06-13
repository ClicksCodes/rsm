import os
import json
import enum


class Stage(enum.Enum):
    PRODUCTION = enum.auto()
    BETA = enum.auto()
    DEV = enum.auto()


class Config:
    def __init__(self, config_file):
        with open(config_file) as config:
            self.config = json.load(config)
        try:
            self.stage = Stage[(os.environ.get("PRODUCTION", "DEV")).upper()]
        except KeyError:
            self.stage = Stage.DEV

    def __getattr__(self, item):
        return self.config.get(f"{item}-{self.stage.name.lower()}", self.config[item])


config = Config("config.json")
os.environ["GIT_SSH_COMMAND"] = "ssh -i sshkey -o IdentitiesOnly=yes"
