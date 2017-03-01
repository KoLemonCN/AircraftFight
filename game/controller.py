from game.listener import *
from game.event import *

import pygame

import math

__author__ = 'Lemon'


class AbstractController(Listener):
    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)

    def notify(self, event):
        """
        Receive events posted to the message queue.
        """


#GameKeyboardController
class GameKeyboardController(AbstractController):
    """
    Handles keyboard input.
    """

    def __init__(self, event_manager):
        AbstractController.__init__(self, event_manager)

    #listen for events
    def notify(self, ev):
        """
        Receive events posted to the message queue.
        """

        if isinstance(ev, TickEvent):
            for event in ev.events:
                if event.type == pygame.QUIT:
                    self.event_manager.notify_all(QuitEvent())
                    # handle key down events
                if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.event_manager.notify_all(QuitEvent())
                    else:
                        self.event_manager.notify_all(KeyboardEvent(event))


#GameMouseController
class GameMouseController(AbstractController):
    """
    Handles mouse input.
    """

    DIRECTION_UP = "up"
    DIRECTION_DOWN = "down"
    DIRECTION_LEFT = "left"
    DIRECTION_RIGHT = "right"
    PYGAME_MOUSE_EVENT_TYPES = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]
    MOUSE_STATE_DEFAULT = "default"
    MOUSE_STATE_DRAG = "drag"
    MOUSE_STATE_PRESSED = "pressed"

    def __init__(self, event_manager):
        AbstractController.__init__(self, event_manager)
        self.mouse_state = self.MOUSE_STATE_DEFAULT
        self.mouse_pos = pygame.mouse.get_pos()
        self.threshold = 10

    #listen for events
    def notify(self, ev):
        """
        Receive events posted to the message queue.
        """
        if isinstance(ev, TickEvent):
            for event in ev.events:
                if event.type in self.PYGAME_MOUSE_EVENT_TYPES:
                    self.__update_mouse_state(event)

    #update the mouse state if the mouse clicked
    def __update_mouse_state(self, event):
        pressed, _, _ = pygame.mouse.get_pressed()

        if not pressed:
            self.notify_all(MouseHoverEvent(pygame.mouse.get_pos()))

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_pos = pygame.mouse.get_pos()
            self.mouse_state = self.MOUSE_STATE_PRESSED
            return

        if event.type == pygame.MOUSEMOTION:
            self.mouse_state = self.MOUSE_STATE_DRAG
            return

        if event.type == pygame.MOUSEBUTTONUP:
            self.__generate_event()

    def __generate_event(self):
        x1, y1 = pygame.mouse.get_pos()
        x0, y0 = self.mouse_pos
        distance = math.hypot(x0 - x1, y0 - y1)
        if distance > self.threshold:
            # this is a swipe!
            direction = self.__calculate_direction(x0, y0, x1, y1)
            self.notify_all(MouseSwipeEvent((x0, y0), direction))
        else:
            self.notify_all(MouseClickEvent((x0, y0)))

        self.mouse_state = self.MOUSE_STATE_DEFAULT

    #calculate the direction and then the route could to draw
    def __calculate_direction(self, x0, y0, x1, y1):
        distance_x = x1 - x0
        distance_y = y1 - y0
        if abs(distance_x) > abs(distance_y):
            if distance_x > 0:
                return self.DIRECTION_RIGHT
            else:
                return self.DIRECTION_LEFT
        else:
            if distance_y > 0:
                return self.DIRECTION_DOWN

        return self.DIRECTION_UP
