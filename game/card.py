from dataclasses import dataclass
from typing import Callable, Optional
from game.config import ELEMENT_COUNTERS, COUNTER_DAMAGE_BONUS


@dataclass
class Card:
    id: int
    name: str
    element: str
    base_damage: int
    cost: int
    effect_func: Optional[Callable] = None
    
    def calculate_damage(self, target_element: str) -> int:
        damage = self.base_damage
        if ELEMENT_COUNTERS.get(self.element) == target_element:
            damage += COUNTER_DAMAGE_BONUS
        return damage
    
    def execute_effect(self, caster, target, battle_context):
        if self.effect_func:
            return self.effect_func(caster, target, battle_context)
        return None
    
    def get_info(self) -> dict:
        return {
            "name": self.name,
            "element": self.element,
            "damage": self.base_damage,
            "cost": self.cost
        }


class CardFactory:
    _id_counter = 0
    
    @classmethod
    def _generate_id(cls) -> int:
        cls._id_counter += 1
        return cls._id_counter
    
    @classmethod
    def create_fireball(cls) -> Card:
        def fireball_effect(caster, target, ctx):
            return {"type": "damage", "value": 8}
        
        return Card(
            id=cls._generate_id(),
            name="Fireball",
            element="fire",
            base_damage=8,
            cost=2,
            effect_func=fireball_effect
        )
    
    @classmethod
    def create_flame_strike(cls) -> Card:
        def flame_strike_effect(caster, target, ctx):
            return {"type": "damage", "value": 12}
        
        return Card(
            id=cls._generate_id(),
            name="Flame Strike",
            element="fire",
            base_damage=12,
            cost=3,
            effect_func=flame_strike_effect
        )
    
    @classmethod
    def create_inferno(cls) -> Card:
        def inferno_effect(caster, target, ctx):
            return {"type": "damage", "value": 18}
        
        return Card(
            id=cls._generate_id(),
            name="Inferno",
            element="fire",
            base_damage=18,
            cost=4,
            effect_func=inferno_effect
        )
    
    @classmethod
    def create_water_jet(cls) -> Card:
        def water_jet_effect(caster, target, ctx):
            return {"type": "damage", "value": 7}
        
        return Card(
            id=cls._generate_id(),
            name="Water Jet",
            element="water",
            base_damage=7,
            cost=2,
            effect_func=water_jet_effect
        )
    
    @classmethod
    def create_tidal_wave(cls) -> Card:
        def tidal_wave_effect(caster, target, ctx):
            return {"type": "damage", "value": 11}
        
        return Card(
            id=cls._generate_id(),
            name="Tidal Wave",
            element="water",
            base_damage=11,
            cost=3,
            effect_func=tidal_wave_effect
        )
    
    @classmethod
    def create_tsunami(cls) -> Card:
        def tsunami_effect(caster, target, ctx):
            return {"type": "damage", "value": 16}
        
        return Card(
            id=cls._generate_id(),
            name="Tsunami",
            element="water",
            base_damage=16,
            cost=4,
            effect_func=tsunami_effect
        )
    
    @classmethod
    def create_wind_slash(cls) -> Card:
        def wind_slash_effect(caster, target, ctx):
            return {"type": "damage", "value": 6}
        
        return Card(
            id=cls._generate_id(),
            name="Wind Slash",
            element="wind",
            base_damage=6,
            cost=1,
            effect_func=wind_slash_effect
        )
    
    @classmethod
    def create_storm(cls) -> Card:
        def storm_effect(caster, target, ctx):
            return {"type": "damage", "value": 10}
        
        return Card(
            id=cls._generate_id(),
            name="Storm",
            element="wind",
            base_damage=10,
            cost=2,
            effect_func=storm_effect
        )
    
    @classmethod
    def create_hurricane(cls) -> Card:
        def hurricane_effect(caster, target, ctx):
            return {"type": "damage", "value": 15}
        
        return Card(
            id=cls._generate_id(),
            name="Hurricane",
            element="wind",
            base_damage=15,
            cost=3,
            effect_func=hurricane_effect
        )
    
    @classmethod
    def create_random_card(cls, element: str = None) -> Card:
        import random
        creators = {
            "fire": [cls.create_fireball, cls.create_flame_strike, cls.create_inferno],
            "water": [cls.create_water_jet, cls.create_tidal_wave, cls.create_tsunami],
            "wind": [cls.create_wind_slash, cls.create_storm, cls.create_hurricane]
        }
        
        if element:
            return random.choice(creators[element])()
        else:
            all_creators = creators["fire"] + creators["water"] + creators["wind"]
            return random.choice(all_creators)()
    
    @classmethod
    def create_deck(cls, size: int = 20) -> list:
        deck = []
        cards_per_element = size // 3
        
        for _ in range(cards_per_element):
            deck.append(cls.create_random_card("fire"))
            deck.append(cls.create_random_card("water"))
            deck.append(cls.create_random_card("wind"))
        
        while len(deck) < size:
            deck.append(cls.create_random_card())
        
        import random
        random.shuffle(deck)
        return deck
