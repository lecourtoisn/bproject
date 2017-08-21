class Player:
    def __init__(self, player_id: str, name: str = "noname"):
        self.id = player_id
        self.cash = 10000
        self.name = name

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id
