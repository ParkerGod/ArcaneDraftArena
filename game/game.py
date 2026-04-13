from typing import Dict, Optional
import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game.states import GameState, StartState, BattleState, ResultState


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("ArcaneDraftArena")
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.states: Dict[str, GameState] = {}
        self.current_state: Optional[GameState] = None
        
        self.result_data = {
            "winner": None,
            "turns": 0,
            "player_hp": 0,
            "ai_hp": 0
        }
        
        self._init_states()
    
    def _init_states(self):
        self.states["start"] = StartState(self)
        self.states["battle"] = BattleState(self)
        self.states["result"] = ResultState(self)
        
        self.transition_to("start")
    
    def transition_to(self, state_name: str):
        if self.current_state:
            self.current_state.exit()
        
        self.current_state = self.states[state_name]
        self.current_state.enter()
    
    def set_result(self, winner: str, turns: int, player_hp: int, ai_hp: int):
        self.result_data = {
            "winner": winner,
            "turns": turns,
            "player_hp": player_hp,
            "ai_hp": ai_hp
        }
    
    def get_result(self) -> dict:
        return self.result_data
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    if self.current_state:
                        self.current_state.handle_event(event)
            
            if self.current_state:
                self.current_state.update(dt)
                self.current_state.render(self.screen)
            
            pygame.display.flip()
        
        pygame.quit()
