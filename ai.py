import random
from models import ELEMENT_ADVANTAGE, Element


class SimpleAI:
    def __init__(self, player):
        self.player = player

    def make_decision(self, battle):
        playable_cards = [
            card for card in self.player.hand
            if card.cost <= self.player.energy
        ]

        if not playable_cards or (random.random() < 0.2 and len(self.player.hand) < 5):
            return "draw", None

        best_card = None
        best_score = -1

        for card in playable_cards:
            score = self._score_card(card, battle)
            if score > best_score:
                best_score = score
                best_card = card

        if best_card:
            return "play", best_card
        return "draw", None

    def _score_card(self, card, battle):
        score = card.damage * 2

        if battle.defending_card:
            defender_element = battle.defending_card.element
            if ELEMENT_ADVANTAGE[card.element] == defender_element:
                score += 10
            elif ELEMENT_ADVANTAGE[defender_element] == card.element:
                score -= 5

        score -= card.cost

        if card.element == Element.WATER and self.player.hp < 15:
            score += 8

        if card.element == Element.WIND and len(self.player.hand) < 3:
            score += 5

        return score
