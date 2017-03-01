__author__ = 'Lemon'

from game.model import *
from game.view import *
from game.controller import *
import pickle
from game.utility import *
import random
import os

class RouteDesignMode(AbstractView):
    STATE_RECORD = 1
    STATE_STOP = 2
    #RouteDesignMode constructor function and initialization
    def __init__(self, manager, parent_view, padding=(50, 100, 50, 100), width=800, height=1000, color=(50, 50, 50)):
        AbstractView.__init__(self, manager, parent_view, width, height, color)
        self.color = color
        self.record_state = self.STATE_STOP
        self.top, self.right, self.bottom, self.left = padding
        self.text = "(0, 0)"
        self.font = pygame.font.Font(None, 30)
        self.states = []
        self.mouse_states = []
        self.route = None
        self.game_rect = [self.left, self.top, self.rect.width-self.left*2, self.rect.height-self.top*2]
        self.info = ""
        self.info_data = "Press 'R' to start. Click to record, 'Space' to shoot."

        self.__load_routes()

    #open the route file
    def __load_routes(self):
        try:
            with open('route_file.prg', 'rb') as route_file:
                self.route_manager = pickle.load(route_file)
        except:
            self.route_manager = RouteManager()

    #listen for events
    def notify(self, ev):
        if isinstance(ev, KeyboardEvent):
            self.__handle_keyboard_event(ev)
        elif isinstance(ev, ButtonClickedEvent):
            self.__handle_click_event(ev)
        elif isinstance(ev, NumberChangedEvent):
            self.load(ev.number)
        #if isinstance(ev, TickEvent):
        #    self.__handle_hover_event(ev)
        elif isinstance(ev, MouseHoverEvent):
            self.__handle_hover_event(ev)
        elif isinstance(ev, MouseClickEvent):
            self.__handle_mouse_click_event(ev)

    #handle mouse click event
    def __handle_mouse_click_event(self, ev):
        if self.record_state == self.STATE_STOP:
            return

        x, y = ev.pos
        if not self.mouse_states:
            self.mouse_states.append([x, y, 0])
            self.states.append([x-self.left, y-self.top, 0])
            return

        last_mouse_states_x, last_mouse_states_y, _ = self.mouse_states[-1]
        last_states_x, last_states_y, _ = self.states[-1]

        # for mouse states
        #delta_x = (x - last_mouse_states_x)
        #delta_y = (y - last_mouse_states_y)
        #ratio = float(delta_y) / delta_x
        mouse_route = StraightRoute(last_mouse_states_x, last_mouse_states_y, x, y)
        self.mouse_states.extend(mouse_route.states)

        state_route = StraightRoute(last_states_x, last_states_y, x-self.left, y-self.top)
        self.states.extend(state_route.states)

    #handle click event
    def __handle_click_event(self, ev):
        button = ev.source

        if button.name == "delete":
            self.delete(button.number_input.number)
        if button.name == "load":
            self.load(button.number_input.number)
        if button.name == "save":
            self.save()
        if button.name == "info":
            self.toggle_info()
        if button.name == "clear":
            self.states = []
            self.mouse_states = []
            self.route = []
        if button.name == "show":
            self.route = []
        if button.name == "replay":
            self.route = Route(self.mouse_states, step=1)

    #handle keyboard event
    def __handle_keyboard_event(self, ev):
        if ev.ev.type == pygame.KEYDOWN:
            # listen key input
            key_pressed = pygame.key.get_pressed()
            # if player dead nothing would happened
            if key_pressed[K_SPACE]:
                self.shoot()
            elif key_pressed[K_r]:
                self.states = []
                self.mouse_states = []
                self.route = []
                self.record_state = self.STATE_RECORD
            elif key_pressed[K_p]:
                self.route = Route(self.mouse_states, step=1)

        elif ev.ev.type == pygame.KEYUP:
            if ev.ev.key == K_r:
                self.record_state = self.STATE_STOP

    #to record the shoot position
    def shoot(self):
        if self.record_state != self.STATE_RECORD:
            return

        self.states[-1][2] = 1
        self.mouse_states[-1][2] = 1

    #handle hover event
    def __handle_hover_event(self, ev):
        mouse_pos = pygame.mouse.get_pos()
        self.text = "({x},{y})".format(x=mouse_pos[0]-self.left, y=mouse_pos[1]-self.top)

        #if self.record_state == self.STATE_STOP:
        #    return

        #self.mouse_states.append([mouse_pos[0], mouse_pos[1], 0])
        #self.states.append([mouse_pos[0]-self.left, mouse_pos[1]-self.top, 0])

    #update and redraw the route
    def update(self, *args):
        self.image.fill(pygame.Color("grey"))
        pygame.draw.rect(self.image, pygame.Color("black"), self.game_rect)
        self.__draw_route()
        text = self.font.render(self.text, True, (255, 0, 0))
        self.image.blit(text, [10, 10])
        text = self.font.render(self.info, True, (0, 0, 0))
        self.image.blit(text, [200, 10])

    #draw the route if user click the mouse
    def __draw_route(self):
        if not self.route:
            for pos in self.mouse_states:
                self.__draw_position(pos)
        else:
            pos = self.route.get_next()
            if pos:
                self.__draw_position(pos)
            else:
                self.route.reset()

    #draw the position
    def __draw_position(self, state):
        if state[2] == 1:
            pygame.draw.circle(self.image, pygame.Color("red"), [state[0], state[1]], 10)
        else:
            pygame.draw.circle(self.image, pygame.Color("green"), [state[0], state[1]], 4)

    def toggle_info(self):
        if self.info:
            self.info = ""
        else:
            self.info = self.info_data

    #save the data which user got to the prg file
    def save(self):
        if self.states:
            route = Route(self.states)
            self.route_manager.add_route(route)
            self.__save_file()

    #load the file user can get the data which they designed before
    def load(self, index):
        route = self.route_manager.get_route(index)
        self.route = []
        self.mouse_states = []
        self.states = []
        if not route:
            return
        self.states = route.states

        for i in range(route.length()):
            state = route.get(i)
            self.mouse_states.append([state[0] + self.left, state[1] + self.top, state[2]])

    #delete the data from the prg file
    def delete(self, index):
        self.route_manager.delete_route(index)
        self.__save_file()

        route = self.route_manager.get_route(index)
        self.states = []
        self.route = []
        self.mouse_states = []
        if not route:
            return
        for i in range(route.length()):
            state = route.get(i)
            self.mouse_states.append([state[0] + self.left, state[1] + self.top, state[2]])

    #save route
    def __save_file(self):
        with open('route_file.prg', 'wb') as route_file:
            pickle.dump(self.route_manager, route_file, pickle.HIGHEST_PROTOCOL)
#run
def main():
    manager = EventManager()
    view = EmptyView(manager, width=800, height=1000)

    game_engine = GameEngine(manager)
    keyboard_controller = GameKeyboardController(manager)
    mouse_controller = GameMouseController(manager)

    design = RouteDesignMode(manager, view)
    view.add_view(design)
    #button info
    button_instruction = Button(manager, view, "info", "info")
    button_instruction.rect.left = 5
    button_instruction.rect.top = 50
    button_clear = Button(manager, view, "clear", "clear")
    button_clear.rect.left = 5
    button_clear.rect.top = 110
    button_replay = Button(manager, view, "replay", "replay")
    button_replay.rect.left = 5
    button_replay.rect.top = 170
    button_show = Button(manager, view, "show", "show")
    button_show.rect.left = 5
    button_show.rect.top = 230
    button_save = Button(manager, view, "save", "save")
    button_save.rect.left = 5
    button_save.rect.top = 290
    button_load = Button(manager, view, "load", "load")
    button_load.rect.left = 5
    button_load.rect.top = 450
    button_delete = Button(manager, view, "delete", "delete")
    button_delete.rect.left = 5
    button_delete.rect.top = 510

    #add button view
    view.add_view(button_instruction)
    view.add_view(button_clear)
    view.add_view(button_replay)
    view.add_view(button_show)
    view.add_view(button_save)
    view.add_view(button_load)
    view.add_view(button_delete)

    number_input = NumberInputView(manager, view, width=50, height=20)
    number_input.rect.left = 20
    number_input.rect.top = 570
    button_load.number_input = number_input
    view.add_view(number_input)
    button_delete.number_input = number_input
    view.add_view(number_input)

    game_engine.start_game()

if __name__ == "__main__":
    main()