__author__ = 'Lemon'

import math

#GameInstance
class GameInstance(object):
    SCREEN_SIZE = [600, 900]

    def __init__(self):
        pass

#RouteManager
class RouteManager(object):
    def __init__(self):
        self.routes = []

    def add_route(self, route):
        self.routes.append(route)

    def get_route(self, index):
        if 0 <= index < len(self.routes):
            return self.routes[index]

    def delete_route(self, index):
        if 0 <= index < len(self.routes):
            return self.routes.pop(index)

    def __str__(self):
        if self.routes:
            return self.routes.__str__()
        return "[]"

#Route
class Route(object):
    def __init__(self, states, step=1):
        self.states = states
        self.step = step
        self.index = -1

    def reset(self):
        self.index = -1

    def get_next(self):
        self.index += 1
        if self.index * self.step < len(self.states):
            return self.states[int(self.index * self.step)]

    def get(self, index):
        return self.states[index]

    def __str__(self):
        ss = ""
        for s in self.states:
            ss += s.__str__() + " "
        return ss

    def add_route(self, route):
        self.states.extend(route.route)

    def length(self):
        return len(self.states)

    def copy(self):
        states = self.states[:]
        return Route(states, self.step)

#RouteSemetric
class RouteSemetric(Route):
    def __init__(self, states, step=1, semetry_x=300, semetry_y=None):
        Route.__init__(self, states, step)
        self.semetry_x = semetry_x
        self.semetry_y = semetry_y
        self.__update_route()

    def __update_route(self):
        for pos in self.states:
            x, y = pos
            if self.semetry_x:
                x = 2 * self.semetry_x - x
            if self.semetry_y:
                y = 2 * self.semetry_y - y
            pos[0] = x
            pos[1] = y


#StraightRoute
class StraightRoute(object):
    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0 = x0, y0
        self.x1, self.y1 = x1, y1
        self.states = []
        self.__update_route()

    def __update_route(self):
        delta_x = self.x1 - self.x0
        delta_y = self.y1 - self.y0
        dist = int(math.hypot(delta_x, delta_y))
        x_step = float(delta_x) / dist
        y_step = float(delta_y) / dist

        position = [self.x0, self.y0]
        #self.states.append([position[0], position[1], 0])
        for i in range(dist):
            position[0] += x_step
            position[1] += y_step
            self.states.append([position[0], position[1], 0])

        for state in self.states:
            x, y, _ = state
            state[0] = int(x)
            state[1] = int(y)




