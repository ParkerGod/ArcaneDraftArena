import pygame
import sys
import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Callable

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 80, 80)
BLUE = (80, 150, 255)
GREEN = (80, 200, 80)
YELLOW = (255, 220, 80)
ORANGE = (255, 150, 50)
PURPLE = (180, 80, 255)
CYAN = (80, 220, 220)

FIRE_COLOR = (255, 100, 50)
WATER_COLOR = (50, 150, 255)
WIND_COLOR = (150, 255, 100)


class ElementType(Enum):
    FIRE = "火"
    WATER = "水"
    WIND = "风"


class GameState(Enum):
    START = auto()
    BATTLE = auto()
    RESULT = auto()


class ActionType(Enum):
    DRAW = auto()
    PLAY = auto()


@dataclass
class CardEffect:
    damage: int = 0
    heal: int = 0
    draw: int = 0
    
    def apply(self, caster, target, battle):
        target.hp -= self.damage
        caster.hp = min(caster.max_hp, caster.hp + self.heal)
        for _ in range(self.draw):
            caster.draw_card(battle.card_pool)


class Card:
    def __init__(self, element: ElementType, name: str, cost: int, effect: CardEffect):
        self.element = element
        self.name = name
        self.cost = cost
        self.effect = effect
    
    def get_element_color(self):
        if self.element == ElementType.FIRE:
            return FIRE_COLOR
        elif self.element == ElementType.WATER:
            return WATER_COLOR
        else:
            return WIND_COLOR
    
    def __repr__(self):
        return f"{self.name}({self.element.value})"


class CardPool:
    def __init__(self):
        self.cards: List[Card] = []
        self._init_cards()
    
    def _init_cards(self):
        fire_cards = [
            Card(ElementType.FIRE, "火球术", 2, CardEffect(damage=15)),
            Card(ElementType.FIRE, "烈焰斩", 3, CardEffect(damage=25)),
            Card(ElementType.FIRE, "炎爆", 4, CardEffect(damage=35)),
            Card(ElementType.FIRE, "火焰护盾", 2, CardEffect(heal=10)),
            Card(ElementType.FIRE, "燃烧", 1, CardEffect(damage=8)),
        ]
        water_cards = [
            Card(ElementType.WATER, "水箭", 2, CardEffect(damage=12)),
            Card(ElementType.WATER, "激流", 3, CardEffect(damage=22)),
            Card(ElementType.WATER, "海啸", 4, CardEffect(damage=32)),
            Card(ElementType.WATER, "治疗波", 2, CardEffect(heal=15)),
            Card(ElementType.WATER, "涌泉", 1, CardEffect(damage=6, heal=5)),
        ]
        wind_cards = [
            Card(ElementType.WIND, "风刃", 2, CardEffect(damage=14)),
            Card(ElementType.WIND, "旋风", 3, CardEffect(damage=24)),
            Card(ElementType.WIND, "风暴", 4, CardEffect(damage=34)),
            Card(ElementType.WIND, "疾风步", 2, CardEffect(draw=1)),
            Card(ElementType.WIND, "微风", 1, CardEffect(damage=7, draw=1)),
        ]
        self.cards = fire_cards + water_cards + wind_cards
    
    def draw_random(self) -> Optional[Card]:
        if self.cards:
            return random.choice(self.cards)
        return None


class Character:
    def __init__(self, name: str, max_hp: int, max_mp: int, is_player: bool = False, element: ElementType = ElementType.FIRE):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.max_mp = max_mp
        self.mp = max_mp
        self.mp_regen = 2
        self.element = element
        self.hand: List[Card] = []
        self.is_player = is_player
        self.has_drawn_this_turn = False
        self.has_played_this_turn = False
    
    def draw_card(self, card_pool: CardPool) -> bool:
        if len(self.hand) >= 7:
            return False
        card = card_pool.draw_random()
        if card:
            self.hand.append(card)
            return True
        return False
    
    def start_turn(self):
        self.mp = min(self.max_mp, self.mp + self.mp_regen)
        self.has_drawn_this_turn = False
        self.has_played_this_turn = False
    
    def can_draw(self) -> bool:
        return not self.has_drawn_this_turn and not self.has_played_this_turn and len(self.hand) < 7
    
    def can_play_card(self, card_index: int) -> bool:
        if self.has_drawn_this_turn or self.has_played_this_turn:
            return False
        if card_index < 0 or card_index >= len(self.hand):
            return False
        return self.hand[card_index].cost <= self.mp
    
    def play_card(self, card_index: int, target, battle) -> bool:
        if not self.can_play_card(card_index):
            return False
        card = self.hand.pop(card_index)
        self.mp -= card.cost
        self.has_played_this_turn = True
        
        damage_multiplier = ElementSystem.get_element_advantage(card.element, target.element)
        original_damage = card.effect.damage
        modified_effect = CardEffect(
            damage=int(original_damage * damage_multiplier),
            heal=card.effect.heal,
            draw=card.effect.draw
        )
        modified_effect.apply(self, target, battle)
        
        battle.add_battle_log(f"{self.name} 使用 {card.name} 对 {target.name} 造成 {modified_effect.damage} 点伤害!")
        if modified_effect.damage > original_damage:
            battle.add_battle_log("  克制! 伤害增加!")
        elif modified_effect.damage < original_damage and original_damage > 0:
            battle.add_battle_log("  被克制! 伤害减少!")
        
        return True
    
    def take_damage(self, damage: int):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
    
    def is_alive(self) -> bool:
        return self.hp > 0


class ElementSystem:
    @staticmethod
    def get_damage_multiplier(card_element: ElementType, target) -> float:
        return 1.0
    
    @staticmethod
    def get_element_advantage(attacker: ElementType, defender: ElementType) -> float:
        if attacker == ElementType.FIRE and defender == ElementType.WIND:
            return 1.5
        if attacker == ElementType.WIND and defender == ElementType.WATER:
            return 1.5
        if attacker == ElementType.WATER and defender == ElementType.FIRE:
            return 1.5
        
        if attacker == ElementType.FIRE and defender == ElementType.WATER:
            return 0.75
        if attacker == ElementType.WATER and defender == ElementType.WIND:
            return 0.75
        if attacker == ElementType.WIND and defender == ElementType.FIRE:
            return 0.75
        
        return 1.0


class AIController:
    def __init__(self, character: Character):
        self.character = character
    
    def decide_action(self, player: Character, card_pool: CardPool) -> tuple:
        can_draw = self.character.can_draw()
        playable_cards = [(i, card) for i, card in enumerate(self.character.hand) 
                         if self.character.can_play_card(i)]
        
        if not can_draw and not playable_cards:
            return ("pass", None)
        
        if playable_cards:
            best_card_idx = self._evaluate_cards(playable_cards, player)
            if best_card_idx is not None:
                return ("play", best_card_idx)
        
        if can_draw:
            return ("draw", None)
        
        return ("pass", None)
    
    def _evaluate_cards(self, playable_cards: List[tuple], player: Character) -> Optional[int]:
        best_score = -999
        best_idx = None
        
        for idx, card in playable_cards:
            score = 0
            
            multiplier = ElementSystem.get_element_advantage(card.element, player.element)
            
            score += card.effect.damage * multiplier
            score += card.effect.heal * 0.8
            score += card.effect.draw * 5
            
            if card.effect.damage > 0:
                if player.hp <= card.effect.damage * multiplier:
                    score += 50
            
            if score > best_score:
                best_score = score
                best_idx = idx
        
        return best_idx


class BattleSystem:
    def __init__(self):
        self.card_pool = CardPool()
        self.player = Character("玩家", 100, 10, True, ElementType.FIRE)
        self.ai = Character("AI对手", 100, 10, False, ElementType.WATER)
        self.ai_controller = AIController(self.ai)
        self.current_turn = "player"
        self.turn_count = 1
        self.battle_logs: List[str] = []
        self.winner: Optional[str] = None
        self._init_battle()
    
    def _init_battle(self):
        for _ in range(3):
            self.player.draw_card(self.card_pool)
            self.ai.draw_card(self.card_pool)
        self.player.start_turn()
        self.add_battle_log("战斗开始!")
        self.add_battle_log("规则: 火克风, 风克水, 水克火")
        self.add_battle_log("每回合只能抽牌或出牌")
    
    def add_battle_log(self, message: str):
        self.battle_logs.append(message)
        if len(self.battle_logs) > 20:
            self.battle_logs.pop(0)
    
    def player_draw(self) -> bool:
        if self.current_turn != "player":
            return False
        if not self.player.can_draw():
            return False
        if self.player.draw_card(self.card_pool):
            self.player.has_drawn_this_turn = True
            self.add_battle_log(f"{self.player.name} 抽了一张牌")
            self.end_player_turn()
            return True
        return False
    
    def player_play_card(self, card_index: int) -> bool:
        if self.current_turn != "player":
            return False
        if self.player.play_card(card_index, self.ai, self):
            self.check_battle_end()
            if self.winner is None:
                self.end_player_turn()
            return True
        return False
    
    def end_player_turn(self):
        self.current_turn = "ai"
        self.ai.start_turn()
    
    def ai_turn(self):
        if self.current_turn != "ai":
            return
        
        action, param = self.ai_controller.decide_action(self.player, self.card_pool)
        
        if action == "draw":
            if self.ai.draw_card(self.card_pool):
                self.add_battle_log(f"{self.ai.name} 抽了一张牌")
        elif action == "play" and param is not None:
            self.ai.play_card(param, self.player, self)
            self.check_battle_end()
        else:
            self.add_battle_log(f"{self.ai.name} 跳过回合")
        
        if self.winner is None:
            self.current_turn = "player"
            self.turn_count += 1
            self.player.start_turn()
    
    def check_battle_end(self):
        if not self.ai.is_alive():
            self.winner = "player"
            self.add_battle_log("玩家获胜!")
        elif not self.player.is_alive():
            self.winner = "ai"
            self.add_battle_log("AI获胜!")


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.SysFont("simhei", 48)
        self.font_medium = pygame.font.SysFont("simhei", 32)
        self.font_small = pygame.font.SysFont("simhei", 20)
        self.font_tiny = pygame.font.SysFont("simhei", 16)
    
    def clear(self):
        self.screen.fill(DARK_GRAY)
    
    def draw_start_screen(self):
        self.clear()
        title = self.font_large.render("Arcane Draft Arena", True, YELLOW)
        subtitle = self.font_medium.render("元素卡牌对战", True, WHITE)
        hint = self.font_small.render("点击任意处开始游戏", True, LIGHT_GRAY)
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 250))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 320))
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 450))
        
        rules = [
            "规则说明:",
            "火克风, 风克水, 水克火",
            "每回合只能抽牌或出牌",
            "击败对手获得胜利!"
        ]
        y = 520
        for rule in rules:
            text = self.font_small.render(rule, True, GRAY)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
            y += 30
    
    def draw_card(self, card: Card, x: int, y: int, width: int = 100, height: int = 140, selected: bool = False):
        color = card.get_element_color()
        
        if selected:
            pygame.draw.rect(self.screen, YELLOW, (x-3, y-3, width+6, height+6), border_radius=8)
        
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=5)
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height), 2, border_radius=5)
        
        name_text = self.font_tiny.render(card.name, True, WHITE)
        self.screen.blit(name_text, (x + 5, y + 5))
        
        element_text = self.font_tiny.render(card.element.value, True, WHITE)
        self.screen.blit(element_text, (x + 5, y + 25))
        
        cost_text = self.font_small.render(str(card.cost), True, YELLOW)
        self.screen.blit(cost_text, (x + width - 25, y + 5))
        
        desc_y = y + 50
        if card.effect.damage > 0:
            dmg_text = self.font_tiny.render(f"伤害:{card.effect.damage}", True, WHITE)
            self.screen.blit(dmg_text, (x + 5, desc_y))
            desc_y += 18
        if card.effect.heal > 0:
            heal_text = self.font_tiny.render(f"治疗:{card.effect.heal}", True, GREEN)
            self.screen.blit(heal_text, (x + 5, desc_y))
            desc_y += 18
        if card.effect.draw > 0:
            draw_text = self.font_tiny.render(f"抽牌:{card.effect.draw}", True, CYAN)
            self.screen.blit(draw_text, (x + 5, desc_y))
    
    def draw_character(self, character: Character, x: int, y: int, is_player: bool = True):
        width = 200
        height = 120
        
        color = BLUE if is_player else RED
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=10)
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height), 2, border_radius=10)
        
        name_text = self.font_medium.render(character.name, True, WHITE)
        self.screen.blit(name_text, (x + 10, y + 10))
        
        hp_width = 180
        hp_height = 20
        hp_ratio = character.hp / character.max_hp
        hp_color = GREEN if hp_ratio > 0.5 else (YELLOW if hp_ratio > 0.25 else RED)
        
        pygame.draw.rect(self.screen, GRAY, (x + 10, y + 50, hp_width, hp_height))
        pygame.draw.rect(self.screen, hp_color, (x + 10, y + 50, int(hp_width * hp_ratio), hp_height))
        pygame.draw.rect(self.screen, WHITE, (x + 10, y + 50, hp_width, hp_height), 1)
        
        hp_text = self.font_small.render(f"HP: {character.hp}/{character.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (x + 10, y + 75))
        
        mp_text = self.font_small.render(f"MP: {character.mp}/{character.max_mp}", True, CYAN)
        self.screen.blit(mp_text, (x + 10, y + 95))
    
    def draw_battle_screen(self, battle: BattleSystem, selected_card_idx: Optional[int] = None):
        self.clear()
        
        turn_text = self.font_medium.render(f"回合 {battle.turn_count} - {'玩家回合' if battle.current_turn == 'player' else 'AI回合'}", True, YELLOW)
        self.screen.blit(turn_text, (SCREEN_WIDTH//2 - turn_text.get_width()//2, 10))
        
        self.draw_character(battle.ai, 50, 80, False)
        self.draw_character(battle.player, SCREEN_WIDTH - 250, 500, True)
        
        element_hint = self.font_small.render("克制关系: 火→风→水→火", True, LIGHT_GRAY)
        self.screen.blit(element_hint, (SCREEN_WIDTH//2 - element_hint.get_width()//2, 80))
        
        hand_y = 650
        for i, card in enumerate(battle.player.hand):
            x = 50 + i * 110
            selected = (i == selected_card_idx)
            self.draw_card(card, x, hand_y, selected=selected)
        
        log_x = 300
        log_y = 220
        log_width = 600
        log_height = 250
        pygame.draw.rect(self.screen, BLACK, (log_x, log_y, log_width, log_height))
        pygame.draw.rect(self.screen, GRAY, (log_x, log_y, log_width, log_height), 2)
        
        log_title = self.font_small.render("战斗日志", True, YELLOW)
        self.screen.blit(log_title, (log_x + 10, log_y + 5))
        
        y = log_y + 30
        for log in battle.battle_logs[-10:]:
            log_text = self.font_tiny.render(log, True, WHITE)
            self.screen.blit(log_text, (log_x + 10, y))
            y += 22
        
        button_y = 720
        if battle.current_turn == "player":
            can_draw = battle.player.can_draw()
            draw_color = GREEN if can_draw else GRAY
            pygame.draw.rect(self.screen, draw_color, (900, button_y, 120, 50), border_radius=5)
            draw_text = self.font_small.render("抽牌 (D)", True, WHITE)
            self.screen.blit(draw_text, (920, button_y + 12))
            
            can_play = selected_card_idx is not None and battle.player.can_play_card(selected_card_idx)
            play_color = ORANGE if can_play else GRAY
            pygame.draw.rect(self.screen, play_color, (1050, button_y, 120, 50), border_radius=5)
            play_text = self.font_small.render("出牌 (S)", True, WHITE)
            self.screen.blit(play_text, (1070, button_y + 12))
        else:
            waiting_text = self.font_medium.render("AI思考中...", True, YELLOW)
            self.screen.blit(waiting_text, (950, button_y + 10))
    
    def draw_result_screen(self, winner: str, battle: BattleSystem):
        self.clear()
        
        if winner == "player":
            result_text = "胜利!"
            color = GREEN
        else:
            result_text = "失败!"
            color = RED
        
        title = self.font_large.render(result_text, True, color)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 250))
        
        stats = [
            f"总回合数: {battle.turn_count}",
            f"剩余HP: {battle.player.hp}/{battle.player.max_hp}",
        ]
        y = 350
        for stat in stats:
            text = self.font_medium.render(stat, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
            y += 50
        
        hint = self.font_small.render("点击任意处返回主菜单", True, LIGHT_GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 500))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Arcane Draft Arena")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.state = GameState.START
        self.battle: Optional[BattleSystem] = None
        self.selected_card_idx: Optional[int] = None
        self.ai_think_timer = 0
    
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)
            
            self.update(dt)
            self.draw()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def handle_event(self, event: pygame.event.Event):
        if self.state == GameState.START:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                self.start_battle()
        
        elif self.state == GameState.BATTLE:
            if self.battle and self.battle.current_turn == "player":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    hand_y = 650
                    for i in range(len(self.battle.player.hand)):
                        card_x = 50 + i * 110
                        if card_x <= mouse_x <= card_x + 100 and hand_y <= mouse_y <= hand_y + 140:
                            self.selected_card_idx = i
                            break
                    
                    button_y = 720
                    if 900 <= mouse_x <= 1020 and button_y <= mouse_y <= button_y + 50:
                        self.battle.player_draw()
                        self.selected_card_idx = None
                    elif 1050 <= mouse_x <= 1170 and button_y <= mouse_y <= button_y + 50:
                        if self.selected_card_idx is not None:
                            if self.battle.player_play_card(self.selected_card_idx):
                                self.selected_card_idx = None
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        self.battle.player_draw()
                        self.selected_card_idx = None
                    elif event.key == pygame.K_s:
                        if self.selected_card_idx is not None:
                            if self.battle.player_play_card(self.selected_card_idx):
                                self.selected_card_idx = None
                    elif event.key == pygame.K_1:
                        self.selected_card_idx = 0
                    elif event.key == pygame.K_2:
                        self.selected_card_idx = 1 if len(self.battle.player.hand) > 1 else None
                    elif event.key == pygame.K_3:
                        self.selected_card_idx = 2 if len(self.battle.player.hand) > 2 else None
                    elif event.key == pygame.K_4:
                        self.selected_card_idx = 3 if len(self.battle.player.hand) > 3 else None
                    elif event.key == pygame.K_5:
                        self.selected_card_idx = 4 if len(self.battle.player.hand) > 4 else None
        
        elif self.state == GameState.RESULT:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                self.state = GameState.START
    
    def start_battle(self):
        self.battle = BattleSystem()
        self.state = GameState.BATTLE
        self.selected_card_idx = None
        self.ai_think_timer = 0
    
    def update(self, dt: float):
        if self.state == GameState.BATTLE and self.battle:
            if self.battle.winner:
                self.state = GameState.RESULT
            elif self.battle.current_turn == "ai":
                self.ai_think_timer += dt
                if self.ai_think_timer >= 1.0:
                    self.battle.ai_turn()
                    self.ai_think_timer = 0
    
    def draw(self):
        if self.state == GameState.START:
            self.renderer.draw_start_screen()
        elif self.state == GameState.BATTLE and self.battle:
            self.renderer.draw_battle_screen(self.battle, self.selected_card_idx)
        elif self.state == GameState.RESULT and self.battle:
            self.renderer.draw_result_screen(self.battle.winner, self.battle)


if __name__ == "__main__":
    game = Game()
    game.run()
