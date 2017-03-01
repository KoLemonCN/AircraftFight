__author__ = 'Lemon'

#Listener
class Listener(object):
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.add_listener(self)

    # this method will be called as a listener being notified
    def notify(self, ev):
        pass
        #print "{}: get event <{}>".format(self.__class__.__name__, ev)

    # use this method to send event to all interested listeners in event manager
    def notify_all(self, event):
        self.event_manager.notify_all(event)


def main():
    print "listner.py test"


if __name__ == "__main__":
    main()

