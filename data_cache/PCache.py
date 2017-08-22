import json
import traceback
from typing import Optional

from shutil import copyfile

from os import remove

import blackjack.Player

db_path = "data_cache/db.json"
backup_db_path = "data_cache/db_backup.json"


class PCache:
    cache = {}

    @classmethod
    def load_all(cls):
        with open(db_path) as f:
            data = json.load(f)
            for p in data.values():
                cls.add(p)

    @classmethod
    def dump_all(cls):
        copyfile(db_path, backup_db_path)
        try:
            with open(db_path, "w+") as f:
                data = {p.id: {
                    "id": p.id,
                    "name": p.name,
                    "cash": p.cash
                } for p in cls.cache.values()}
                json.dump(data, f)
        except Exception:
            traceback.print_exc()
            copyfile(backup_db_path, db_path)
            remove(backup_db_path)

    @classmethod
    def add(cls, player: "blackjack.Player.Player"):
        if player.id not in cls.cache:
            cls.cache[player.id] = player

    @classmethod
    def has(cls, player_id) -> bool:
        return player_id in cls.cache

    @classmethod
    def get(cls, player_id) -> "Optional[blackjack.Player.Player]":
        player = cls.cache.get(player_id, None)
        if player is None:
            player = blackjack.Player.Player(player_id)
            cls.add(player)
        return player

