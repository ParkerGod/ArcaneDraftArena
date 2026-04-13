import pygame
import sys
from state_base import BaseState
from constants import GameState
from game_states import StartState, BattleState, ResultState


class Game:
    def __init__(self):
        pygame.init()
        self.width = 1280
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Arcane Draft Arena")
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        try:
            self.font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 32)
            self.large_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 64)
            self.small_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 20)
            self.card_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 24)
        except:
            self.font = pygame.font.SysFont("simsun, simhei, microsoftyahei, arial", 32)
            self.large_font = pygame.font.SysFont("simsun, simhei, microsoftyahei, arial", 64)
            self.small_font = pygame.font.SysFont("simsun, simhei, microsoftyahei, arial", 20)
            self.card_font = pygame.font.SysFont("simsun, simhei, microsoftyahei, arial", 24)

        self.state_machine = StateMachine(self)
        self.state_machine.change_state(GameState.START)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.state_machine.current_state.handle_event(event)

    def update(self):
        self.state_machine.current_state.update()

    def render(self):
        self.screen.fill((30, 30, 50))
        self.state_machine.current_state.render(self.screen)
        pygame.display.flip()


class StateMachine:
    def __init__(self, game):
        self.game = game
        self.current_state = None
        self.states = {
            GameState.START: StartState(game),
            GameState.BATTLE: BattleState(game),
            GameState.RESULT: ResultState(game)
        }

    def change_state(self, new_state):
        if self.current_state:
            self.current_state.exit()
        self.current_state = self.states[new_state]
        self.current_state.enter()


if __name__ == "__main__":
    game = Game()
    game.run()
