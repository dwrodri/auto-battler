import json
from typing import List, Dict, Any


def load_data(file_name: str) -> Dict[str, Dict[str, Any]]:
    with open(file_name, "r") as fp:
        return json.load(fp)


SUPER_AUTO_PETS: Dict[str, Dict[str, Any]] = load_data("../sample_data.json")


class Pet:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data
        self.status_effect = None


class Player:
    def __init__(self) -> None:
        self.health = 15
        self.gold = 10
        self.pet_slots: List[Pet] = []
    
class Store:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

class SAPVersusMode:
    def __init__(self) -> None:
        self.players = [Player() for _ in range(2)]

    def do_turn(self):
        pass
