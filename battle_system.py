import random
from models import Player, create_deck, ELEMENT_ADVANTAGE
from ai import SimpleAI


class TurnPhase:
    DRAW = "draw"
    ACTION = "action"
    END = "end"


class Battle:
    def __init__(self):
        self.player = Player("玩家")
        self.ai = Player("AI对手", is_ai=True)
        self.ai_controller = SimpleAI(self.ai)
        self.current_player = self.player
        self.opponent = self.ai
        self.turn = 1
        self.phase = TurnPhase.ACTION
        self.log = []
        self.defending_card = None
        self.game_over = False
        self.winner = None
        self.selected_card = None
        self.animating = False

        self._init_decks()

    def _init_decks(self):
        self.player.deck = create_deck()
        self.ai.deck = create_deck()
        self.player.draw_card(4)
        self.ai.draw_card(4)
        self.log.append("战斗开始！")

    def start_new_turn(self):
        self.turn += 1
        self.current_player, self.opponent = self.opponent, self.current_player
        self.current_player.restore_energy()
        self.current_player.has_acted = False
        self.defending_card = None
        self.log.append(f"--- 第 {self.turn} 回合：{self.current_player.name} 回合 ---")

        if self.current_player.is_ai:
            self._execute_ai_turn()

    def player_draw_card(self):
        if self.current_player.has_acted:
            return False, "本回合已经行动过了！"

        if not self.current_player.deck:
            return False, "牌库已空！"

        if len(self.current_player.hand) >= 7:
            return False, "手牌已满！"

        self.current_player.draw_card(1)
        self.current_player.has_acted = True
        self.log.append(f"{self.current_player.name} 抽了一张牌")
        return True, ""

    def player_play_card(self, card):
        if self.current_player.has_acted:
            return False, "本回合已经行动过了！"

        if card.cost > self.current_player.energy:
            return False, "能量不足！"

        self.current_player.energy -= card.cost
        self.current_player.hand.remove(card)
        self.current_player.has_acted = True

        card.apply_effect(self, self.current_player, self.opponent)
        self.defending_card = card

        self._check_game_over()
        return True, ""

    def _execute_ai_turn(self):
        action, card = self.ai_controller.make_decision(self)
        
        if action == "draw":
            self.ai.draw_card(1)
            self.log.append(f"{self.ai.name} 抽了一张牌")
        elif action == "play" and card:
            self.ai.energy -= card.cost
            self.ai.hand.remove(card)
            card.apply_effect(self, self.ai, self.player)
            self.defending_card = card
            self._check_game_over()
        
        self.ai.has_acted = True
        
        if not self.game_over:
            self.start_new_turn()

    def _check_game_over(self):
        if self.player.hp <= 0:
            self.game_over = True
            self.winner = self.ai
            self.log.append(f"{self.ai.name} 获胜！")
        elif self.ai.hp <= 0:
            self.game_over = True
            self.winner = self.player
            self.log.append(f"{self.player.name} 获胜！")

    def end_turn(self):
        if not self.current_player.has_acted:
            return False, "必须先抽牌或出牌！"
        return True, ""
