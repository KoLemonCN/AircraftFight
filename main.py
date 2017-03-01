__author__ = 'Lemon'

from game.model import *
from game.view import *
from game.controller import *
#run game
def main():
    pygame.init()
    pygame.mixer.init()
    manager = EventManager()
    game_engine = GameEngine(manager)
    keyboard_controller = GameKeyboardController(manager)
    mouse_controller = GameMouseController(manager)
    view = MainView(manager)

    game_engine.start_game()


if __name__ == "__main__":
    main()



