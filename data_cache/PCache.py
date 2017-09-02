import json
import os
import traceback
from typing import Optional

from shutil import copyfile

from os import remove

import blackjack.Player


def check_file(func):
    def wrapper(cls, *_, **kwargs):
        if not cls.db_path or not cls.backup_db_path:
            raise (Exception("No score file specified"))
        if not os.path.exists(cls.db_path):
            with open(cls.db_path, "w+") as f:
                json.dump({}, f)

        return func(cls, *_, **kwargs)

    return wrapper


class PCache:
    db_path = None
    backup_db_path = None
    cache = {}

    @classmethod
    def set_paths(cls, db_path, backup_db_path):
        cls.db_path = db_path
        cls.backup_db_path = backup_db_path

    @classmethod
    @check_file
    def load_all(cls):
        with open(cls.db_path) as f:
            data = json.load(f)
            for p in data.values():
                cls.add(blackjack.Player.Player(p["id"], p["name"], p["cash"]))

    @classmethod
    @check_file
    def dump_all(cls):
        copyfile(cls.db_path, cls.backup_db_path)
        try:
            with open(cls.db_path, "w+") as f:
                data = {p.id: {
                    "id": p.id,
                    "name": p.name,
                    "cash": p.cash
                } for p in cls.cache.values()}
                json.dump(data, f)
        except Exception:
            traceback.print_exc()
            copyfile(cls.backup_db_path, cls.db_path)
            remove(cls.backup_db_path)

    @classmethod
    @check_file
    def add(cls, player: "blackjack.Player.Player"):
        if player.id not in cls.cache:
            cls.cache[player.id] = player

    @classmethod
    @check_file
    def has(cls, player_id) -> bool:
        return player_id in cls.cache

    @classmethod
    @check_file
    def get(cls, player_id) -> "Optional[blackjack.Player.Player]":
        player = cls.cache.get(player_id, None)
        if player is None:
            player = blackjack.Player.Player(player_id)
            cls.add(player)
        return player
