__author__ = 'Lemon'

#class event
class Event(object):
    def __init__(self, name=""):
        if not name:
            self.name = self.__class__.__name__
        else:
            self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


#GameModelInitializedEvent
class GameModelInitializedEvent(Event):
    def __init__(self):
        Event.__init__(self)

#QuitEvent
class QuitEvent(Event):
    def __init__(self):
        Event.__init__(self)

#TickEvent
class TickEvent(Event):
    def __init__(self, events):
        Event.__init__(self)
        self.events = events

#KeyboardEvent
class KeyboardEvent(Event):
    def __init__(self, ev):
        Event.__init__(self)
        self.ev = ev

    def __str__(self):
        return "{}: {}".format(self.name, self.ev)

#NumberChangedEvent
class NumberChangedEvent(Event):
    def __init__(self, number):
        Event.__init__(self)
        self.number = number

#MouseClickEvent
class MouseClickEvent(Event):
    def __init__(self, pos):
        Event.__init__(self)
        self.pos = pos

    def __str__(self):
        return "{}: {}".format(self.name, self.pos)

#MouseHoverEvent
class MouseHoverEvent(Event):
    def __init__(self, pos):
        Event.__init__(self)
        self.pos = pos

    def __str__(self):
        return "{}: {}".format(self.name, self.pos)

#MouseSwipeEvent
class MouseSwipeEvent(Event):
    def __init__(self, pos, direction):
        Event.__init__(self)
        self.pos = pos
        self.direction = direction

    def __str__(self):
        return "{}: {} {}".format(self.name, self.pos, self.direction)

#TextUpdateEvent
class TextUpdateEvent(Event):
    def __init__(self, text):
        Event.__init__(self)
        self.text = text

#ButtonClickedEvent
class ButtonClickedEvent(Event):
    def __init__(self, source):
        Event.__init__(self)
        self.source = source

#GameStartedEvent
class GameStartedEvent(Event):
    def __init__(self):
        Event.__init__(self)

#GameDifficultyChangedEvent
class GameDifficultyChangedEvent(Event):
    def __init__(self, difficulty):
        Event.__init__(self)
        self.difficulty = difficulty

#GameWelcomeEvent
class GameWelcomeEvent(Event):
    def __init__(self):
        Event.__init__(self)

#PlayerScoreChangedEvent
class PlayerScoreChangedEvent(Event):
    def __init__(self, score):
        Event.__init__(self)
        self.score = score

#PlayerHpChangedEvent
class PlayerHpChangedEvent(Event):
    def __init__(self, hp):
        Event.__init__(self)
        self.hp = hp

#PlayerLifeChangedEvent
class PlayerLifeChangedEvent(Event):
    def __init__(self, life):
        Event.__init__(self)
        self.life = life

#GameOverEvent
class GameOverEvent(Event):
    def __init__(self):
        Event.__init__(self)

#GamePlayerShipChangedEvent
class GamePlayerShipChangedEvent(Event):
    def __init__(self, ship_name):
        Event.__init__(self)
        self.ship_name = ship_name

#EventManager
class EventManager(object):
    def __init__(self):
        from weakref import WeakKeyDictionary

        self.listeners = WeakKeyDictionary()

#add_listener
    def add_listener(self, listener):
        self.listeners[listener] = 1

#remove_listener
    def remove_listener(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]
#notify_all
    def notify_all(self, event):
        if not isinstance(event, TickEvent):
            pass
        for listener in self.listeners.keys():
            listener.notify(event)


def main():
    event = Event()

if __name__ == "__main__":
    main()
