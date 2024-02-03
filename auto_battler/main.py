import json
import random
import sys
from typing import Any, Dict, List, Tuple

DEFAULT_COST = 3
DEFAULT_MAX_PET_COUNT = 5


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
        self.experience = 0
        self.status = None
        self.cost = kwargs["cost"] if "cost" in kwargs.keys() else DEFAULT_COST
        self.name: str = kwargs["name"]
        self.identifier = kwargs["id"]
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

    def upgrade(self, other) -> None:
        assert other.identifier == self.identifier
        self.base_health = max(self.base_health, other.base_health) + 1
        self.base_attack = max(self.base_attack, other.base_attack) + 1
        self.experience += other.experience
        if self.experience < 2:
            self.level = 1
        elif self.experience < 5:
            self.level = 2
        else:
            self.level = 3


class Food:
    def __init__(self, **kwargs) -> None:
        self.name = kwargs["name"]
        self.identifier = kwargs["id"]
        self.icon = kwargs["image"]["unicodeCodePoint"]
        self.tier = kwargs["tier"]
        self.ability = Ability(**kwargs["ability"])
        self.cost = kwargs["cost"] if "cost" in kwargs.keys() else DEFAULT_COST


class Player:
    def __init__(self) -> None:
        self.health: int = 15
        self.coins: int = 10
        self.pets: List[Pet] = []
        self.frozen_pets: List[Pet] = []
        self.frozen_foods: List[Food] = []


class Store:
    def __init__(self, **kwargs) -> None:
        self.pets: Dict[str, Dict[str, Any]] = kwargs["pets"]
        self.foods: Dict[str, Dict[str, Any]] = kwargs["foods"]
        self.turns: Dict[str, Dict[str, Any]] = kwargs["turns"]

    def get_roll(
        self, turn: int, frozen_pets: List[Pet] = [], frozen_foods: List[Food] = []
    ) -> Tuple[List[Pet], List[Food]]:
        pet_ids = [
            pet["id"]
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
            food["id"]
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
            frozen_pets
            + [
                Pet(**self.pets[choice])
                for choice in random.choices(
                    pet_ids,
                    weights=pet_weights,
                    k=self.turns[f"turn-{turn}"]["animalShopSlots"] - len(frozen_pets),
                )
            ],
            frozen_foods
            + [
                Food(**self.foods[choice])
                for choice in random.choices(
                    food_ids,
                    weights=food_weights,
                    k=self.turns[f"turn-{turn}"]["foodShopSlots"] - len(frozen_foods),
                )
            ],
        )


class CLIAgent:
    def make_store_choice(
        self, p: Player, shop_pets: List[Pet], shop_foods: List[Food]
    ) -> bool:
        """
        Control Logic for updating a player state in a store
        """
        done = False
        print(f"Pets: {[pet.icon for pet in p.pets]} 💰: {p.coins}")
        print(
            f"Stats    : {[str(pet.base_health) + '  ' + str(pet.base_attack) for pet in p.pets]}"
        )
        print(
            f"Shop Pets: {[' ' + pet.icon + ' ' for pet in shop_pets]} Shop Foods: {[food.icon for food in shop_foods]}"
        )
        valid_input = False
        while not valid_input:
            userin = input("Choose from [P]et / [F]ood / [R]oll / [S]ell / [D]one:")
            # Purchase Pet
            if userin[0].lower() == "p":
                if shop_pets:
                    userin_choice = int(
                        input(f"Choose from index [0 - {len(shop_pets)}): ")
                    )
                    if userin_choice < len(shop_pets) and p.coins > DEFAULT_COST:
                        chosen_pet = shop_pets[int(userin_choice)]
                        can_fuse = chosen_pet.identifier in [
                            pet.identifier for pet in p.pets
                        ]
                        chosen_slot = int(input(f"Choose from index [0 - 5)"))
                        if (
                            can_fuse or len(p.pets) < DEFAULT_MAX_PET_COUNT
                        ) and chosen_slot < 5:
                            if p.pets[chosen_slot].identifier == chosen_pet.identifier:
                                p.pets[chosen_slot].upgrade(chosen_pet)
                            else:
                                p.pets.insert(chosen_slot, chosen_pet)
                            p.coins -= DEFAULT_COST
            # Purchase Food
            elif userin[0].lower() == "f":
                if shop_foods:
                    userin_choice = int(
                        input(f"Choose from index [0 - {len(shop_foods)}): ")
                    )
                    if (
                        userin_choice < len(shop_foods)
                        and p.coins > shop_foods[userin_choice].cost
                    ):
                        pass
            elif userin[0].lower() == "r":
                pass
            elif userin[0].lower() == "d":
                done = True
        return done


class SAPVersusMode:
    def __init__(self, num_players: int) -> None:
        self.players = [Player() for _ in range(num_players)]
        self.agents = [CLIAgent() for _ in range(num_players)]
        self.store = Store(**SUPER_AUTO_PETS)

    def apply_effect(self):
        pass

    def trigger(self, name: str):
        targets = []
        for player in self.players:
            for pet in player.pets:
                if pet.abilities[pet.level - 1].trigger == name:
                    targets.append(pet)
        print(f"effects to apply: {targets}")

    def shop_phase(self, player: Player, turn: int):
        player.coins = 10
        self.trigger("StartOfTurn")
        pets, foods = self.store.get_roll(turn, player.frozen_pets, player.frozen_foods)

        self.trigger("EndOfTurn")

    def play(self):
        for player in self.players:
            for turn in range(1, 2):
                self.shop_phase(player, turn)


if __name__ == "__main__":
    SAPVersusMode(2).play()
