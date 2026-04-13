from typing import List, Optional, Tuple
from game.card import Card
from game.player import Player
from game.config import ELEMENT_COUNTERS


class AIController:
    def __init__(self, ai_player: Player, opponent: Player):
        self.ai_player = ai_player
        self.opponent = opponent
    
    def evaluate_card(self, card: Card) -> float:
        score = 0.0
        
        damage = card.calculate_damage(self._guess_opponent_element())
        score += damage * 2
        
        if self._has_element_advantage(card.element):
            score += 10
        
        efficiency = damage / card.cost if card.cost > 0 else damage
        score += efficiency * 3
        
        if self.ai_player.hp < 10:
            score += damage * 0.5
        
        return score
    
    def _guess_opponent_element(self) -> str:
        if not self.opponent.hand:
            return "fire"
        
        element_counts = {}
        for card in self.opponent.hand:
            element_counts[card.element] = element_counts.get(card.element, 0) + 1
        
        if element_counts:
            return max(element_counts, key=element_counts.get)
        return "fire"
    
    def _has_element_advantage(self, card_element: str) -> bool:
        opponent_main = self._guess_opponent_element()
        return ELEMENT_COUNTERS.get(card_element) == opponent_main
    
    def choose_action(self) -> Tuple[str, Optional[Card]]:
        playable_cards = self.ai_player.get_playable_cards()
        
        if not playable_cards:
            return ("draw", None)
        
        if len(self.ai_player.hand) < 4 and self.ai_player.deck:
            if len(self.ai_player.hand) <= 2:
                return ("draw", None)
        
        best_card = self._select_best_card(playable_cards)
        
        if best_card:
            return ("play", best_card)
        
        return ("draw", None)
    
    def _select_best_card(self, playable_cards: List[Card]) -> Optional[Card]:
        if not playable_cards:
            return None
        
        scored_cards = [(card, self.evaluate_card(card)) for card in playable_cards]
        scored_cards.sort(key=lambda x: x[1], reverse=True)
        
        return scored_cards[0][0]
    
    def select_target_card(self) -> Optional[Card]:
        if not self.opponent.hand:
            return None
        
        playable = [c for c in self.opponent.hand]
        if not playable:
            return None
        
        return playable[0]
