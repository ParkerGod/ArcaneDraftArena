from abc import ABC, abstractmethod
from typing import Optional
import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY, RED, GREEN, BLUE, YELLOW, ELEMENT_COLORS
from game.player import Player
from game.card import CardFactory
from game.ai import AIController


class GameState(ABC):
    def __init__(self, game):
        self.game = game
    
    @abstractmethod
    def enter(self):
        pass
    
    @abstractmethod
    def exit(self):
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass
    
    @abstractmethod
    def update(self, dt: float):
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface):
        pass


class StartState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = None
        self.button_font = None
        self.start_button = None
        self.hover_start = False
    
    def enter(self):
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 48)
        button_width = 200
        button_height = 60
        self.start_button = pygame.Rect(
            SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT // 2 + 50,
            button_width,
            button_height
        )
    
    def exit(self):
        pass
    
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.hover_start = self.start_button.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.collidepoint(event.pos):
                self.game.transition_to("battle")
    
    def update(self, dt: float):
        pass
    
    def render(self, screen: pygame.Surface):
        screen.fill(DARK_GRAY)
        
        title_text = self.title_font.render("ArcaneDraftArena", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title_text, title_rect)
        
        subtitle_font = pygame.font.Font(None, 36)
        subtitle_text = subtitle_font.render("Element Card Battle", True, LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50))
        screen.blit(subtitle_text, subtitle_rect)
        
        self._draw_element_legend(screen)
        
        button_color = GREEN if self.hover_start else GRAY
        pygame.draw.rect(screen, button_color, self.start_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.start_button, 2, border_radius=10)
        
        start_text = self.button_font.render("START", True, WHITE)
        text_rect = start_text.get_rect(center=self.start_button.center)
        screen.blit(start_text, text_rect)
        
        self._draw_rules(screen)
    
    def _draw_element_legend(self, screen: pygame.Surface):
        legend_font = pygame.font.Font(None, 28)
        legend_y = SCREEN_HEIGHT // 2 - 80
        
        elements = [
            ("Fire > Wind", ELEMENT_COLORS["fire"], 200),
            ("Wind > Water", ELEMENT_COLORS["wind"], 450),
            ("Water > Fire", ELEMENT_COLORS["water"], 700)
        ]
        
        for text, color, x in elements:
            pygame.draw.circle(screen, color, (x - 30, legend_y), 12)
            legend_text = legend_font.render(text, True, WHITE)
            screen.blit(legend_text, (x - 10, legend_y - 10))
    
    def _draw_rules(self, screen: pygame.Surface):
        rules_font = pygame.font.Font(None, 24)
        rules = [
            "Rules:",
            "- Each turn: Draw a card OR Play a card",
            "- Counter elements deal +5 bonus damage",
            "- Reduce opponent HP to 0 to win",
            "- Game ends after 20 turns (highest HP wins)"
        ]
        
        start_y = SCREEN_HEIGHT - 150
        for i, rule in enumerate(rules):
            color = YELLOW if i == 0 else LIGHT_GRAY
            text = rules_font.render(rule, True, color)
            screen.blit(text, (50, start_y + i * 25))


class BattleState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.player = None
        self.ai_player = None
        self.ai_controller = None
        self.turn = 1
        self.current_actor = "player"
        self.action_taken = False
        self.selected_card = None
        self.message = ""
        self.message_timer = 0
        self.game_over = False
        self.winner = None
        self.font = None
        self.small_font = None
        self.card_rects = []
        self.draw_button = None
        self.hover_card = -1
        self.hover_draw = False
        self.ai_thinking = False
        self.ai_think_timer = 0
    
    def enter(self):
        self.player = Player("Player")
        self.ai_player = Player("AI", is_ai=True)
        
        self.player.deck = CardFactory.create_deck(20)
        self.ai_player.deck = CardFactory.create_deck(20)
        
        for _ in range(4):
            self.player.draw_card()
            self.ai_player.draw_card()
        
        self.ai_controller = AIController(self.ai_player, self.player)
        
        self.player.restore_energy()
        self.ai_player.restore_energy()
        
        self.turn = 1
        self.current_actor = "player"
        self.action_taken = False
        self.selected_card = None
        self.game_over = False
        self.winner = None
        self.message = "Your turn! Draw or play a card."
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.draw_button = pygame.Rect(50, 450, 120, 40)
    
    def exit(self):
        pass
    
    def handle_event(self, event: pygame.event.Event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                self.game.transition_to("result")
            return
        
        if self.current_actor != "player" or self.action_taken:
            return
        
        if event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)
    
    def _update_hover(self, pos):
        self.hover_card = -1
        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(pos):
                self.hover_card = i
                break
        
        self.hover_draw = self.draw_button.collidepoint(pos)
    
    def _handle_click(self, pos):
        if self.draw_button.collidepoint(pos):
            self._player_draw()
            return
        
        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(pos):
                if i < len(self.player.hand):
                    card = self.player.hand[i]
                    if self.player.can_play_card(card):
                        self._player_play_card(card)
                return
    
    def _player_draw(self):
        if self.action_taken:
            self.message = "Already took action this turn!"
            return
        
        card = self.player.draw_card()
        if card:
            self.message = f"Drew {card.name}!"
            self.action_taken = True
            self._end_player_turn()
        else:
            self.message = "Cannot draw! Deck empty or hand full."
    
    def _player_play_card(self, card):
        if self.action_taken:
            self.message = "Already took action this turn!"
            return
        
        played_card = self.player.play_card(card.id)
        if played_card:
            damage = played_card.calculate_damage("fire")
            self.ai_player.take_damage(damage)
            
            advantage = self._check_element_advantage(played_card.element, "fire")
            self.message = f"Played {played_card.name}! Dealt {damage} damage{advantage}"
            self.action_taken = True
            self._check_game_over()
            
            if not self.game_over:
                self._end_player_turn()
    
    def _check_element_advantage(self, attacker_element, defender_element):
        from game.config import ELEMENT_COUNTERS
        if ELEMENT_COUNTERS.get(attacker_element) == defender_element:
            return " (COUNTER!)"
        return ""
    
    def _end_player_turn(self):
        self.current_actor = "ai"
        self.action_taken = False
        self.ai_thinking = True
        self.ai_think_timer = 1.0
        self.message = "AI is thinking..."
    
    def update(self, dt: float):
        if self.message_timer > 0:
            self.message_timer -= dt
        
        if self.game_over:
            return
        
        if self.current_actor == "ai" and self.ai_thinking:
            self.ai_think_timer -= dt
            if self.ai_think_timer <= 0:
                self._execute_ai_turn()
        
        self._update_card_rects()
    
    def _execute_ai_turn(self):
        self.ai_thinking = False
        
        action, card = self.ai_controller.choose_action()
        
        if action == "draw":
            drawn = self.ai_player.draw_card()
            if drawn:
                self.message = f"AI drew a card."
            else:
                self.message = "AI cannot draw."
        elif action == "play" and card:
            played = self.ai_player.play_card(card.id)
            if played:
                damage = played.calculate_damage("fire")
                self.player.take_damage(damage)
                self.message = f"AI played {played.name}! Dealt {damage} damage."
        
        self._check_game_over()
        
        if not self.game_over:
            self._end_round()
    
    def _end_round(self):
        self.turn += 1
        
        if self.turn > 20:
            self._determine_winner_by_hp()
            return
        
        self.player.restore_energy()
        self.ai_player.restore_energy()
        self.current_actor = "player"
        self.action_taken = False
        self.message = f"Turn {self.turn} - Your turn!"
    
    def _check_game_over(self):
        if not self.player.is_alive():
            self.game_over = True
            self.winner = "AI"
            self.message = "Game Over! AI wins!"
            self.game.set_result("AI", self.turn, self.player.hp, self.ai_player.hp)
        elif not self.ai_player.is_alive():
            self.game_over = True
            self.winner = "Player"
            self.message = "Victory! You win!"
            self.game.set_result("Player", self.turn, self.player.hp, self.ai_player.hp)
    
    def _determine_winner_by_hp(self):
        self.game_over = True
        if self.player.hp > self.ai_player.hp:
            self.winner = "Player"
            self.message = "Time's up! You win by HP!"
        elif self.ai_player.hp > self.player.hp:
            self.winner = "AI"
            self.message = "Time's up! AI wins by HP!"
        else:
            self.winner = "Draw"
            self.message = "Time's up! It's a draw!"
        
        self.game.set_result(self.winner, self.turn, self.player.hp, self.ai_player.hp)
    
    def _update_card_rects(self):
        self.card_rects = []
        start_x = 200
        y = 580
        spacing = 110
        
        for i in range(len(self.player.hand)):
            rect = pygame.Rect(start_x + i * spacing, y, 100, 140)
            self.card_rects.append(rect)
    
    def render(self, screen: pygame.Surface):
        screen.fill(DARK_GRAY)
        
        self._draw_hp_bars(screen)
        self._draw_turn_info(screen)
        self._draw_message(screen)
        self._draw_ai_hand(screen)
        self._draw_player_hand(screen)
        self._draw_deck_info(screen)
        self._draw_action_buttons(screen)
        
        if self.game_over:
            self._draw_game_over(screen)
    
    def _draw_hp_bars(self, screen: pygame.Surface):
        bar_width = 200
        bar_height = 25
        
        player_bar_x = 50
        player_bar_y = 50
        pygame.draw.rect(screen, GRAY, (player_bar_x, player_bar_y, bar_width, bar_height))
        hp_ratio = self.player.hp / self.player.max_hp
        pygame.draw.rect(screen, GREEN, (player_bar_x, player_bar_y, int(bar_width * hp_ratio), bar_height))
        pygame.draw.rect(screen, WHITE, (player_bar_x, player_bar_y, bar_width, bar_height), 2)
        
        hp_text = self.small_font.render(f"Player HP: {self.player.hp}/{self.player.max_hp}", True, WHITE)
        screen.blit(hp_text, (player_bar_x, player_bar_y - 25))
        
        energy_text = self.small_font.render(f"Energy: {self.player.energy}/{self.player.max_energy}", True, YELLOW)
        screen.blit(energy_text, (player_bar_x, player_bar_y + 30))
        
        ai_bar_x = SCREEN_WIDTH - 250
        ai_bar_y = 50
        pygame.draw.rect(screen, GRAY, (ai_bar_x, ai_bar_y, bar_width, bar_height))
        ai_hp_ratio = self.ai_player.hp / self.ai_player.max_hp
        pygame.draw.rect(screen, RED, (ai_bar_x, ai_bar_y, int(bar_width * ai_hp_ratio), bar_height))
        pygame.draw.rect(screen, WHITE, (ai_bar_x, ai_bar_y, bar_width, bar_height), 2)
        
        ai_hp_text = self.small_font.render(f"AI HP: {self.ai_player.hp}/{self.ai_player.max_hp}", True, WHITE)
        screen.blit(ai_hp_text, (ai_bar_x, ai_bar_y - 25))
        
        ai_energy_text = self.small_font.render(f"Energy: {self.ai_player.energy}/{self.ai_player.max_energy}", True, YELLOW)
        screen.blit(ai_energy_text, (ai_bar_x, ai_bar_y + 30))
    
    def _draw_turn_info(self, screen: pygame.Surface):
        turn_text = self.font.render(f"Turn: {self.turn}/20", True, WHITE)
        screen.blit(turn_text, (SCREEN_WIDTH // 2 - 50, 20))
        
        actor_text = self.small_font.render(f"Current: {self.current_actor.upper()}", True, YELLOW)
        screen.blit(actor_text, (SCREEN_WIDTH // 2 - 60, 55))
    
    def _draw_message(self, screen: pygame.Surface):
        msg_surface = self.font.render(self.message, True, WHITE)
        msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, 400))
        pygame.draw.rect(screen, BLACK, msg_rect.inflate(20, 10))
        screen.blit(msg_surface, msg_rect)
    
    def _draw_ai_hand(self, screen: pygame.Surface):
        start_x = 200
        y = 100
        spacing = 80
        
        for i in range(len(self.ai_player.hand)):
            rect = pygame.Rect(start_x + i * spacing, y, 70, 100)
            pygame.draw.rect(screen, GRAY, rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)
            
            q_text = self.small_font.render("?", True, WHITE)
            q_rect = q_text.get_rect(center=rect.center)
            screen.blit(q_text, q_rect)
    
    def _draw_player_hand(self, screen: pygame.Surface):
        for i, rect in enumerate(self.card_rects):
            if i >= len(self.player.hand):
                break
            
            card = self.player.hand[i]
            can_play = self.player.can_play_card(card)
            
            bg_color = ELEMENT_COLORS[card.element]
            if not can_play:
                bg_color = tuple(c // 2 for c in bg_color)
            
            if self.hover_card == i:
                pygame.draw.rect(screen, WHITE, rect.inflate(6, 6), border_radius=8)
            
            pygame.draw.rect(screen, bg_color, rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)
            
            name_font = pygame.font.Font(None, 20)
            name_text = name_font.render(card.name[:12], True, WHITE)
            screen.blit(name_text, (rect.x + 5, rect.y + 10))
            
            elem_text = self.small_font.render(card.element.capitalize(), True, WHITE)
            screen.blit(elem_text, (rect.x + 5, rect.y + 35))
            
            dmg_text = self.font.render(f"DMG: {card.base_damage}", True, WHITE)
            screen.blit(dmg_text, (rect.x + 5, rect.y + 70))
            
            cost_text = self.small_font.render(f"Cost: {card.cost}", True, YELLOW)
            screen.blit(cost_text, (rect.x + 5, rect.y + 110))
    
    def _draw_deck_info(self, screen: pygame.Surface):
        deck_rect = pygame.Rect(50, 500, 80, 110)
        pygame.draw.rect(screen, GRAY, deck_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, deck_rect, 2, border_radius=5)
        
        deck_text = self.small_font.render("DECK", True, WHITE)
        deck_text_rect = deck_text.get_rect(center=(deck_rect.centerx, deck_rect.y + 20))
        screen.blit(deck_text, deck_text_rect)
        
        count_text = self.font.render(str(len(self.player.deck)), True, WHITE)
        count_rect = count_text.get_rect(center=(deck_rect.centerx, deck_rect.centery + 10))
        screen.blit(count_text, count_rect)
    
    def _draw_action_buttons(self, screen: pygame.Surface):
        if self.current_actor == "player" and not self.action_taken and not self.game_over:
            btn_color = GREEN if self.hover_draw else GRAY
            pygame.draw.rect(screen, btn_color, self.draw_button, border_radius=5)
            pygame.draw.rect(screen, WHITE, self.draw_button, 2, border_radius=5)
            
            draw_text = self.small_font.render("DRAW", True, WHITE)
            text_rect = draw_text.get_rect(center=self.draw_button.center)
            screen.blit(draw_text, text_rect)
    
    def _draw_game_over(self, screen: pygame.Surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        go_font = pygame.font.Font(None, 72)
        go_text = go_font.render("GAME OVER", True, WHITE)
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(go_text, go_rect)
        
        winner_color = GREEN if self.winner == "Player" else RED
        winner_text = self.font.render(f"Winner: {self.winner}", True, winner_color)
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(winner_text, winner_rect)
        
        continue_text = self.small_font.render("Press any key to continue", True, LIGHT_GRAY)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        screen.blit(continue_text, continue_rect)


class ResultState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.winner = None
        self.turns = 0
        self.player_hp = 0
        self.ai_hp = 0
        self.font = None
        self.small_font = None
        self.restart_button = None
        self.hover_restart = False
    
    def enter(self):
        result = self.game.get_result()
        self.winner = result["winner"]
        self.turns = result["turns"]
        self.player_hp = result["player_hp"]
        self.ai_hp = result["ai_hp"]
        
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        
        button_width = 200
        button_height = 50
        self.restart_button = pygame.Rect(
            SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT // 2 + 100,
            button_width,
            button_height
        )
    
    def exit(self):
        pass
    
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.hover_restart = self.restart_button.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.restart_button.collidepoint(event.pos):
                self.game.transition_to("start")
    
    def update(self, dt: float):
        pass
    
    def render(self, screen: pygame.Surface):
        screen.fill(DARK_GRAY)
        
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("BATTLE RESULT", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)
        
        winner_color = GREEN if self.winner == "Player" else RED if self.winner == "AI" else YELLOW
        winner_text = self.font.render(f"Winner: {self.winner}", True, winner_color)
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(winner_text, winner_rect)
        
        stats_y = 280
        stats = [
            f"Total Turns: {self.turns}",
            f"Your Final HP: {self.player_hp}",
            f"AI Final HP: {self.ai_hp}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.small_font.render(stat, True, WHITE)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y + i * 40))
            screen.blit(stat_text, stat_rect)
        
        btn_color = GREEN if self.hover_restart else GRAY
        pygame.draw.rect(screen, btn_color, self.restart_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.restart_button, 2, border_radius=10)
        
        restart_text = self.small_font.render("PLAY AGAIN", True, WHITE)
        text_rect = restart_text.get_rect(center=self.restart_button.center)
        screen.blit(restart_text, text_rect)
