from dataclasses import dataclass, field
from typing import List, Optional
from game.config import PLAYER_HP, MAX_HAND_SIZE
from game.card import Card


@dataclass
class Player:
    name: str
    hp: int = PLAYER_HP
    max_hp: int = PLAYER_HP
    hand: List[Card] = field(default_factory=list)
    deck: List[Card] = field(default_factory=list)
    energy: int = 0
    max_energy: int = 5
    is_ai: bool = False
    
    def draw_card(self) -> Optional[Card]:
        if not self.deck:
            return None
        if len(self.hand) >= MAX_HAND_SIZE:
            return None
        
        card = self.deck.pop(0)
        self.hand.append(card)
        return card
    
    def play_card(self, card_id: int) -> Optional[Card]:
        for i, card in enumerate(self.hand):
            if card.id == card_id:
                if self.energy >= card.cost:
                    self.energy -= card.cost
                    return self.hand.pop(i)
        return None
    
    def can_play_card(self, card: Card) -> bool:
        return self.energy >= card.cost and card in self.hand
    
    def take_damage(self, damage: int) -> int:
        self.hp = max(0, self.hp - damage)
        return self.hp
    
    def heal(self, amount: int) -> int:
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp
    
    def restore_energy(self):
        self.energy = self.max_energy
    
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def get_playable_cards(self) -> List[Card]:
        return [card for card in self.hand if self.energy >= card.cost]
    
    def get_hand_info(self) -> List[dict]:
        return [card.get_info() for card in self.hand]
