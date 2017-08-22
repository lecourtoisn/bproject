import data_cache.PCache


class Player:
    def __init__(self, player_id: str, name: str = None, cash=None):
        self.id = player_id
        self.name = name
        self._cash = cash or 0

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    @property
    def cash(self):
        return self._cash

    @cash.setter
    def cash(self, value):
        self._cash = value
        data_cache.PCache.PCache.dump_all()
