__author__ = 'Lemon'

from game.listener import *
from game.event import *
import pygame

#GameEngine
class GameEngine(Listener):
    def __init__(self, event_manager):
        super(GameEngine, self).__init__(event_manager)

    #listen for the events
    def notify(self, event):
        if isinstance(event, QuitEvent):
            super(GameEngine, self).notify(event)
            self.running = False

    #runnning the game
    def start_game(self):
        """
        Starts the game engine loop.

        This pumps a Tick event into the message queue for each loop.
        The loop ends when this object hears a QuitEvent in notify().
        """
        self.running = True
        self.event_manager.notify_all(GameModelInitializedEvent())
        while self.running:
            tick = TickEvent(pygame.event.get())
            self.event_manager.notify_all(tick)

        self.quit()

    #close the game
    def quit(self):
        pygame.quit()


#TextModel
class TextModel(Listener):
    LEGAL_STR = list("`1234567890-=qwertyuiop[]asdfghjkl;'#zxcvbnm,./\\") + list(
        "!\"$%^&*()_+QWERTYUIOP{}ASDFGHJKL:@~|ZXCVBNM<>? ")

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.text = ""
        self.last_input = ""
        self.time_limit = 30
        self.count = 0

    #listen for the event
    def notify(self, event):
        if isinstance(event, KeyboardEvent):
            #super(TextModel, self).notify(event)
            # your code goes here
            self.update_text(event.ev)

    #if key down text would be updated
    def update_text(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
            elif ev.key == pygame.K_RETURN:
                self.text += "\n"
            else:
                try:
                    s = str(ev.unicode)
                    if s in self.LEGAL_STR:
                        self.text += s
                        self.last_input = ev.key
                except:
                    pass

        self.notify_all(TextUpdateEvent(self.text))

