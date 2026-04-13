import pygame
from constants import GameState
from state_base import BaseState
from battle_system import Battle
from models import ELEMENT_COLORS


class StartState(BaseState):
    def enter(self):
        self.start_button_rect = pygame.Rect(self.game.width // 2 - 150, 400, 300, 80)
        self.hovering = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovering = self.start_button_rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button_rect.collidepoint(event.pos):
                self.game.state_machine.change_state(GameState.BATTLE)

    def update(self):
        pass

    def render(self, screen):
        title = self.game.large_font.render("Arcane Draft Arena", True, (255, 215, 0))
        subtitle = self.game.font.render("奥术卡牌竞技场", True, (200, 200, 200))

        rules = [
            "游戏规则：",
            "• 火克风、风克水、水克火",
            "• 每回合只能选择：抽牌 或 出牌",
            "• 击败对手即可获胜"
        ]

        screen.blit(title, (self.game.width // 2 - title.get_width() // 2, 150))
        screen.blit(subtitle, (self.game.width // 2 - subtitle.get_width() // 2, 230))

        for i, rule in enumerate(rules):
            rule_text = self.game.font.render(rule, True, (180, 180, 180))
            screen.blit(rule_text, (self.game.width // 2 - 200, 280 + i * 40))

        button_color = (100, 150, 100) if self.hovering else (70, 120, 70)
        pygame.draw.rect(screen, button_color, self.start_button_rect, border_radius=15)
        pygame.draw.rect(screen, (150, 200, 150), self.start_button_rect, 3, border_radius=15)

        start_text = self.game.font.render("开始游戏", True, (255, 255, 255))
        screen.blit(start_text, (self.game.width // 2 - start_text.get_width() // 2,
                                 self.start_button_rect.y + start_text.get_height() // 2 + 10))


class BattleState(BaseState):
    def enter(self):
        self.battle = Battle()
        self.draw_button_rect = pygame.Rect(50, 500, 120, 50)
        self.end_turn_button_rect = pygame.Rect(self.game.width - 170, 500, 120, 50)
        self.selected_card_index = None
        self.message = ""
        self.message_timer = 0

    def handle_event(self, event):
        if self.battle.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.game.state_machine.states[GameState.RESULT].winner = self.battle.winner
                self.game.state_machine.change_state(GameState.RESULT)
            return

        if self.battle.current_player.is_ai:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            if self.draw_button_rect.collidepoint(mouse_pos):
                success, msg = self.battle.player_draw_card()
                if not success:
                    self._show_message(msg)
                return

            if self.end_turn_button_rect.collidepoint(mouse_pos):
                success, msg = self.battle.end_turn()
                if success:
                    self.battle.start_new_turn()
                else:
                    self._show_message(msg)
                return

            for i, _ in enumerate(self.battle.player.hand):
                card_rect = self._get_card_rect(i, len(self.battle.player.hand))
                if card_rect.collidepoint(mouse_pos):
                    if self.selected_card_index == i:
                        card = self.battle.player.hand[i]
                        success, msg = self.battle.player_play_card(card)
                        if success:
                            self.selected_card_index = None
                        else:
                            self._show_message(msg)
                    else:
                        self.selected_card_index = i
                    return

    def _show_message(self, msg):
        self.message = msg
        self.message_timer = 120

    def _get_card_rect(self, index, total):
        spacing = 110
        start_x = self.game.width // 2 - (total * spacing) // 2
        return pygame.Rect(start_x + index * spacing, self.game.height - 180, 100, 150)

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1

    def render(self, screen):
        self._render_ai_area(screen)
        self._render_player_area(screen)
        self._render_battle_info(screen)
        self._render_buttons(screen)
        self._render_log(screen)

        if self.message_timer > 0:
            msg_surf = self.game.font.render(self.message, True, (255, 100, 100))
            screen.blit(msg_surf, (self.game.width // 2 - msg_surf.get_width() // 2, 350))

        if self.battle.game_over:
            overlay = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            text = self.game.large_font.render(f"{self.battle.winner.name} 获胜！", True, (255, 215, 0))
            screen.blit(text, (self.game.width // 2 - text.get_width() // 2, 300))
            hint = self.game.font.render("点击继续", True, (200, 200, 200))
            screen.blit(hint, (self.game.width // 2 - hint.get_width() // 2, 380))

    def _render_ai_area(self, screen):
        hp_text = self.game.font.render(f"HP: {self.battle.ai.hp}/{self.battle.ai.max_hp}", True, (255, 100, 100))
        screen.blit(hp_text, (self.game.width - 200, 50))

        name_text = self.game.font.render(self.battle.ai.name, True, (255, 255, 255))
        screen.blit(name_text, (self.game.width - 200, 20))

        card_count = self.game.font.render(f"手牌: {len(self.battle.ai.hand)}", True, (180, 180, 180))
        screen.blit(card_count, (self.game.width - 200, 85))

        deck_count = self.game.font.render(f"牌库: {len(self.battle.ai.deck)}", True, (180, 180, 180))
        screen.blit(deck_count, (self.game.width - 200, 115))

    def _render_player_area(self, screen):
        hp_text = self.game.font.render(f"HP: {self.battle.player.hp}/{self.battle.player.max_hp}", True, (100, 255, 100))
        screen.blit(hp_text, (50, self.game.height - 220))

        name_text = self.game.font.render(self.battle.player.name, True, (255, 255, 255))
        screen.blit(name_text, (50, self.game.height - 250))

        energy_text = self.game.font.render(f"能量: {self.battle.player.energy}/{self.battle.player.max_energy}", True, (100, 200, 255))
        screen.blit(energy_text, (50, self.game.height - 190))

        deck_count = self.game.font.render(f"牌库: {len(self.battle.player.deck)}", True, (180, 180, 180))
        screen.blit(deck_count, (50, self.game.height - 160))

        for i, card in enumerate(self.battle.player.hand):
            self._render_card(screen, card, i, len(self.battle.player.hand), self.selected_card_index == i)

    def _render_card(self, screen, card, index, total, selected):
        rect = self._get_card_rect(index, total)

        if selected:
            rect.y -= 20

        color = ELEMENT_COLORS[card.element]
        pygame.draw.rect(screen, (50, 50, 50), rect, border_radius=8)
        pygame.draw.rect(screen, color, rect, 3, border_radius=8)

        pygame.draw.circle(screen, (100, 150, 255), (rect.x + 15, rect.y + 15), 12)
        cost_text = self.game.font.render(str(card.cost), True, (255, 255, 255))
        screen.blit(cost_text, (rect.x + 10, rect.y + 7))

        name_surf = self.game.card_font.render(card.name, True, (255, 255, 255))
        screen.blit(name_surf, (rect.x + 10, rect.y + 45))

        dmg_surf = self.game.card_font.render(f"伤害: {card.damage}", True, (255, 200, 100))
        screen.blit(dmg_surf, (rect.x + 10, rect.y + 80))

        effect_desc = {
            "fire": "+50% 伤害克制",
            "water": "+2 生命恢复",
            "wind": "+1 抽牌"
        }
        effect_surf = self.game.small_font.render(effect_desc[card.element.value], True, (180, 180, 180))
        screen.blit(effect_surf, (rect.x + 5, rect.y + 115))

    def _render_battle_info(self, screen):
        turn_text = self.game.font.render(f"第 {self.battle.turn} 回合", True, (255, 215, 0))
        screen.blit(turn_text, (self.game.width // 2 - 60, 20))

        current_text = self.game.font.render(f"当前: {self.battle.current_player.name}", True, (255, 255, 255))
        screen.blit(current_text, (self.game.width // 2 - 80, 55))

        if self.battle.defending_card:
            vs_text = self.game.font.render(f"上场: {self.battle.defending_card.name}", True,
                                            ELEMENT_COLORS[self.battle.defending_card.element])
            screen.blit(vs_text, (self.game.width // 2 - 80, 90))

    def _render_buttons(self, screen):
        can_act = not self.battle.current_player.is_ai and not self.battle.current_player.has_acted

        draw_color = (70, 130, 180) if can_act and not self.battle.game_over else (80, 80, 80)
        pygame.draw.rect(screen, draw_color, self.draw_button_rect, border_radius=8)
        draw_text = self.game.font.render("抽牌", True, (255, 255, 255))
        screen.blit(draw_text, (self.draw_button_rect.x + 30, self.draw_button_rect.y + 10))

        end_color = (180, 100, 50) if not self.battle.current_player.is_ai and not self.battle.game_over else (80, 80, 80)
        pygame.draw.rect(screen, end_color, self.end_turn_button_rect, border_radius=8)
        end_text = self.game.font.render("结束回合", True, (255, 255, 255))
        screen.blit(end_text, (self.end_turn_button_rect.x + 10, self.end_turn_button_rect.y + 10))

    def _render_log(self, screen):
        y = 200
        for msg in self.battle.log[-5:]:
            log_surf = self.game.small_font.render(msg, True, (180, 180, 180))
            screen.blit(log_surf, (self.game.width // 2 - 200, y))
            y += 30


class ResultState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.winner = None
        self.restart_button_rect = pygame.Rect(self.game.width // 2 - 150, 400, 300, 80)
        self.hovering = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovering = self.restart_button_rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.restart_button_rect.collidepoint(event.pos):
                self.game.state_machine.change_state(GameState.BATTLE)

    def render(self, screen):
        result_text = "胜利！" if self.winner and not self.winner.is_ai else "失败..."
        result_color = (255, 215, 0) if self.winner and not self.winner.is_ai else (200, 100, 100)

        title = self.game.large_font.render(result_text, True, result_color)
        screen.blit(title, (self.game.width // 2 - title.get_width() // 2, 200))

        button_color = (100, 150, 100) if self.hovering else (70, 120, 70)
        pygame.draw.rect(screen, button_color, self.restart_button_rect, border_radius=15)
        pygame.draw.rect(screen, (150, 200, 150), self.restart_button_rect, 3, border_radius=15)

        restart_text = self.game.font.render("再来一局", True, (255, 255, 255))
        screen.blit(restart_text, (self.game.width // 2 - restart_text.get_width() // 2,
                                   self.restart_button_rect.y + restart_text.get_height() // 2 + 10))
