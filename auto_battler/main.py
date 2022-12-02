import json
import random
import sys
from typing import Any, Dict, List, Tuple


def load_data(file_name: str) -> Dict[str, Dict[str, Any]]:
    with open(file_name, "r") as fp:
        return json.load(fp)


SUPER_AUTO_PETS: Dict[str, Dict[str, Any]] = load_data(sys.argv[1])


class Ability:
    def __init__(self, **kwargs) -> None:
        self.description = kwargs["description"]
        self.trigger = kwargs["trigger"]
        self.triggeredBy = kwargs["triggeredBy"]
        self.effect = kwargs["effect"]


class Pet:
    def __init__(self, **kwargs) -> None:
        self.level: int = 1
        self.status = None
        self.name: str = kwargs["name"]
        self.icon: str = kwargs["image"]["unicodeCodePoint"]
        self.tier: int = kwargs["tier"]
        self.base_attack: int = kwargs["baseAttack"]
        self.base_health: int = kwargs["baseHealth"]
        self.abilities: List[Ability] = [
            Ability(**data)
            for data in [
                kwargs[f"level{i}Ability"]
                for i in range(1, 4)
                if f"level{i}Ability" in kwargs.keys()
            ]
        ]


class Food:
    def __init__(self, **kwargs) -> None:
        self.name = kwargs["name"]
        self.icon = kwargs["image"]["unicodeCodePoint"]
        self.tier = kwargs["tier"]
        self.ability = Ability(**kwargs["ability"])


class Player:
    def __init__(self) -> None:
        self.health: int = 15
        self.coins: int = 10
        self.pets: List[Pet] = []


class Store:
    def __init__(self, **kwargs) -> None:
        self.pets: Dict[str, Dict[str, Any]] = kwargs["pets"]
        self.foods: Dict[str, Dict[str, Any]] = kwargs["foods"]
        self.turns: Dict[str, Dict[str, Any]] = kwargs["turns"]

    def get_roll(self, turn: int) -> Tuple[List[Pet], List[Food]]:
        pet_ids = [
            pet["identifier"]
            for pet in self.pets.values()
            if "StandardPack" in pet["packs"]
            and isinstance(pet["tier"], int)
            and pet["tier"] < self.turns[f"turn-{turn}"]["levelUpTier"]
        ]
        pet_weights = [
            pet["probabilities"][turn - 1]["perSlot"]["StandardPack"]
            for pet in self.pets.values()
            if "StandardPack" in pet["packs"]
            and isinstance(pet["tier"], int)
            and pet["tier"] < self.turns[f"turn-{turn}"]["levelUpTier"]
        ]
        food_ids = [
            food["identifier"]
            for food in self.foods.values()
            if isinstance(food["tier"], int)
            and food["tier"] < self.turns[f"turn-{turn}"]["levelUpTier"]
        ]
        food_weights = [
            food["probabilities"][turn - 1]["perSlot"]["StandardPack"]
            for food in self.foods.values()
            if isinstance(food["tier"], int)
            and food["tier"] < self.turns[f"turn-{turn}"]["levelUpTier"]
        ]
        return (
            [
                Pet(**self.pets[choice])
                for choice in random.choices(
                    pet_ids,
                    weights=pet_weights,
                    k=self.turns[f"turn-{turn}"]["animalShopSlots"],
                )
            ],
            [
                Food(**self.foods[choice])
                for choice in random.choices(
                    food_ids,
                    weights=food_weights,
                    k=self.turns[f"turn-{turn}"]["foodShopSlots"],
                )
            ],
        )


class SAPVersusMode:
    def __init__(self, num_players: int) -> None:
        self.players = [Player() for _ in range(num_players)]

    def apply_effect(self):
        pass

    def trigger(self, name: str):
        for player in self.players:
            for pet in player.pets:
                if pet.abilities[pet.level - 1].trigger == name:
                    print()

    def do_turn(self):
        pass


if __name__ == "__main__":
    s = Store(**SUPER_AUTO_PETS)
    pets, foods = s.get_roll(turn=1)
    print(f"Pets: {[pet.icon for pet in pets]} Foods:{[food.icon for food in foods]}")
