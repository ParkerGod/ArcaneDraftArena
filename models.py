from enum import Enum
import random
from card_effects import FireEffect, WaterEffect, WindEffect


class Element(Enum):
    FIRE = "fire"
    WATER = "water"
    WIND = "wind"


ELEMENT_ADVANTAGE = {
    Element.FIRE: Element.WIND,
    Element.WIND: Element.WATER,
    Element.WATER: Element.FIRE
}

ELEMENT_COLORS = {
    Element.FIRE: (255, 100, 50),
    Element.WATER: (50, 150, 255),
    Element.WIND: (100, 255, 150)
}

ELEMENT_NAMES = {
    Element.FIRE: "火",
    Element.WATER: "水",
    Element.WIND: "风"
}


class Card:
    def __init__(self, element, cost, damage, effect=None):
        self.element = element
        self.cost = cost
        self.damage = damage
        self.effect = effect
        self.name = f"{ELEMENT_NAMES[element]}之卡"

    def apply_effect(self, battle, caster, target):
        if self.effect:
            self.effect.execute(battle, caster, target, self)


class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.max_hp = 30
        self.hp = self.max_hp
        self.max_energy = 3
        self.energy = self.max_energy
        self.hand = []
        self.deck = []
        self.has_acted = False

    def draw_card(self, count=1):
        for _ in range(count):
            if self.deck and len(self.hand) < 7:
                card = self.deck.pop()
                self.hand.append(card)

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)

    def restore_energy(self):
        self.energy = self.max_energy


def create_deck():
    deck = []
    elements = [Element.FIRE, Element.WATER, Element.WIND]
    effects = {
        Element.FIRE: FireEffect(),
        Element.WATER: WaterEffect(),
        Element.WIND: WindEffect()
    }

    for element in elements:
        for _ in range(4):
            deck.append(Card(element, 1, 3, effects[element]))
        for _ in range(3):
            deck.append(Card(element, 2, 5, effects[element]))
        for _ in range(2):
            deck.append(Card(element, 3, 8, effects[element]))

    random.shuffle(deck)
    return deck


def calculate_damage(attacker_card, defender_card):
    base_damage = attacker_card.damage
    if defender_card and ELEMENT_ADVANTAGE[attacker_card.element] == defender_card.element:
        return int(base_damage * 1.5)
    elif defender_card and ELEMENT_ADVANTAGE[defender_card.element] == attacker_card.element:
        return int(base_damage * 0.5)
    return base_damage
