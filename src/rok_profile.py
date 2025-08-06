import os
import pprint
from dataclasses import dataclass
from typing import Dict, List

import yaml

from . import logger
from .const import PROJECT_ROOT


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass
class Character:
    name: str
    ch: int
    assist_interval: int
    rss_order: List[str]
    rss_level: int
    slot_number: int


@dataclass
class Account:
    name: str
    characters: List[str]


class RokProfile(metaclass=SingletonMeta):
    def __init__(self, path=os.path.join(PROJECT_ROOT, "profile.yml")):
        self.path = path
        self.data = {}
        self.rss_orders: Dict[str, List[str]] = {}
        self.accounts: Dict[str, Account] = {}
        self.chars: Dict[str, Character] = {}
        self.action_mode: int = 1
        self.load()

    def load(self):
        logger.info(f"Load RokProfile from {self.path}")
        with open(self.path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

        self.action_mode = self.data.get("action_mode", 1)
        self.rss_orders = self.data.get("rss_orders", {})

        # Load accounts
        for acc_id, acc_data in self.data.get("accounts", {}).items():
            self.accounts[str(acc_id)] = Account(**acc_data)

        # Load chars and resolve rss_order references
        for char_id, char_data in self.data.get("characters", {}).items():
            rss_key = char_data.get("rss_order")
            char_data["rss_order"] = self.rss_orders.get(rss_key, [])
            self.chars[char_id] = Character(**char_data)

    def __repr__(self):
        return pprint.pformat(self.data)

    def __str__(self):
        return self.data

    def get_account(self, acc_id: int) -> Account:
        return self.accounts[acc_id]

    def get_char(self, char_id: str) -> Character:
        return self.chars[char_id]

    def get_char_by_name(self, char_name: str) -> Character | None:
        for char in self.chars.values():
            if char.name == char_name:
                return char

    def get_char_id_by_name(self, char_name: str) -> str | None:
        for char_id, char in self.chars.items():
            if char.name == char_name:
                return char_id

    def all_accounts(self) -> List[str]:
        """Return list of accounts id"""
        return list(self.accounts.keys())

    def all_chars(self) -> List[str]:
        """Return list of characters id"""
        return list(self.chars.keys())
