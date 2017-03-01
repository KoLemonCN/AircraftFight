import threading
import math
import pygame

__author__ = 'Lemon'

#Easing
class Easing(object):
    """
    All functions are available: http://gsgd.co.uk/sandbox/jquery/easing/jquery.easing.1.3.js
    Converted from Javascript, originally used in JQuery to create animations.
    This Easing Class provides easing functions as speed parameter in Animation.
    t: current time, b: begInnIng value, c: change In value, d: duration
    """

    @staticmethod
    def ease_linear(t, b, c, d):
        return c * t / d + b

    @staticmethod
    def ease_in_quad(t, b, c, d):
        t /= d
        return c * t * t + b

    @staticmethod
    def ease_out_quad(t, b, c, d):
        t /= d
        return -c * t * (t - 2) + b

    @staticmethod
    def ease_in_out_quad(t, b, c, d):
        t /= d / 2
        if t < 1:
            return c / 2 * t * t + b
        t -= 1
        return -c / 2 * (t * (t - 2) - 1) + b

    @staticmethod
    def ease_in_cubic(t, b, c, d):
        t /= d
        return c * t * t * t + b

    @staticmethod
    def ease_out_cubic(t, b, c, d):
        t = t / d - 1
        return c * (t * t * t + 1) + b

    @staticmethod
    def ease_in_out_cubic(t, b, c, d):
        t /= d / 2
        if t < 1:
            return c / 2 * t * t * t + b
        t -= 2
        return c / 2 * (t * t * t + 2) + b

    @staticmethod
    def ease_in_quart(t, b, c, d):
        t /= d
        return c * t * t * t * t + b

    @staticmethod
    def ease_out_quart(t, b, c, d):
        t = t / d - 1
        return -c * (t * t * t * t - 1) + b

    @staticmethod
    def ease_in_out_quart(t, b, c, d):
        t /= d / 2
        if t < 1:
            return c / 2 * t * t * t * t + b
        t -= 2
        return -c / 2 * (t * t * t * t - 2) + b

    @staticmethod
    def ease_in_quint(t, b, c, d):
        t /= d
        return c * t * t * t * t * t + b

    @staticmethod
    def ease_out_quint(t, b, c, d):
        t = t / d - 1
        return c * (t * t * t * t * t + 1) + b

    @staticmethod
    def ease_in_out_quint(t, b, c, d):
        t /= d / 2
        if t < 1:
            return c / 2 * t * t * t * t * t + b
        t -= 2
        return c / 2 * (t * t * t * t * t + 2) + b

    @staticmethod
    def ease_in_sine(t, b, c, d):
        return -c * math.cos(t / d * (math.pi / 2)) + c + b

    @staticmethod
    def ease_out_sine(t, b, c, d):
        return c * math.sin(t / d * (math.pi / 2)) + b

    @staticmethod
    def ease_in_out_sine(t, b, c, d):
        return -c / 2 * (math.cos(math.pi * t / d) - 1) + b

    @staticmethod
    def ease_in_expo(t, b, c, d):
        if t == 0:
            return b

        return c * math.pow(2, 10 * (t / d - 1)) + b

    @staticmethod
    def ease_out_expo(t, b, c, d):
        if t == d:
            return b + c
        return c * (-math.pow(2, -10 * t / d) + 1) + b

    @staticmethod
    def ease_in_out_expo(t, b, c, d):
        if t == 0:
            return b
        if t == d:
            return b + c
        t /= d / 2
        if t < 1:
            return c / 2 * math.pow(2, 10 * (t - 1)) + b
        t -= 1
        return c / 2 * (-math.pow(2, -10 * t) + 2) + b

    @staticmethod
    def ease_in_circ(t, b, c, d):
        t /= d
        return -c * (math.sqrt(1 - t * t) - 1) + b

    @staticmethod
    def ease_out_circ(t, b, c, d):
        t = t / d - 1
        return c * math.sqrt(1 - t * t) + b

    @staticmethod
    def ease_in_out_circ(t, b, c, d):
        t /= d / 2
        if t < 1:
            return -c / 2 * (math.sqrt(1 - t * t) - 1) + b
        t -= 2
        return c / 2 * (math.sqrt(1 - t * t) + 1) + b

    @staticmethod
    def ease_in_elastic(t, b, c, d):
        p = d * 0.3
        a = c
        if t == 0:
            return b
        t /= d
        if t == 1:
            return b + c
        if a < abs(c):
            a = c
            s = p / 4
        else:
            s = p / (2 * math.pi) * math.asin(c / a)
        t -= 1
        return -(a * math.pow(2, 10 * t) * math.sin((t * d - s) * (2 * math.pi) / p)) + b

    @staticmethod
    def ease_out_elastic(t, b, c, d):
        p = d * 0.3
        a = c

        if t == 0:
            return b
        t /= d
        if t == 1:
            return b + c
        if a < abs(c):
            a = c
            s = p / 4
        else:
            s = p / (2 * math.pi) * math.asin(c / a)
        return a * math.pow(2, -10 * t) * math.sin((t * d - s) * (2 * math.pi) / p) + c + b

    @staticmethod
    def ease_in_out_elastic(t, b, c, d):
        p = d * (0.3 * 1.5)
        a = c
        if t == 0:
            return b
        t /= d / 2
        if t == 2:
            return b + c
        if a < abs(c):
            a = c
            s = p / 4
        else:
            s = p / (2 * math.pi) * math.asin(c / a)
        if t < 1:
            t -= 1
            return -0.5 * (a * math.pow(2, 10 * t) * math.sin((t * d - s) * (2 * math.pi) / p)) + b
        t -= 1
        return a * math.pow(2, -10 * t) * math.sin((t * d - s) * (2 * math.pi) / p) * 0.5 + c + b

    @staticmethod
    def ease_in_back(t, b, c, d):
        s = 1.70158
        t /= d
        return c * t * t * ((s + 1) * t - s) + b

    @staticmethod
    def ease_out_back(t, b, c, d):
        s = 1.70158
        t = t / d - 1
        return c * (t * t * ((s + 1) * t + s) + 1) + b

    @staticmethod
    def ease_in_out_back(t, b, c, d):
        s = 1.70158
        t /= d / 2
        if t < 1:
            s *= 1.525
            return c / 2 * (t * t * ((s + 1) * t - s)) + b
        t -= 2
        s *= 1.525
        return c / 2 * (t * t * ((s + 1) * t + s) + 2) + b

    @staticmethod
    def ease_in_bounce(t, b, c, d):
        return c - Easing.ease_out_bounce(d - t, 0, c, d) + b

    @staticmethod
    def ease_out_bounce(t, b, c, d):
        t /= d
        if t < (1 / 2.75):
            return c * (7.5625 * t * t) + b
        elif t < (2 / 2.75):
            t -= (1.5 / 2.75)
            return c * (7.5625 * t * t + .75) + b
        elif t < (2.5 / 2.75):
            t -= (2.25 / 2.75)
            return c * (7.5625 * t * t + .9375) + b
        else:
            t -= (2.625 / 2.75)
            return c * (7.5625 * t * t + .984375) + b

    @staticmethod
    def ease_in_out_bounce(t, b, c, d):
        if t < d / 2:
            return Easing.ease_in_bounce(t * 2, 0, c, d) * 0.5 + b
        return Easing.ease_out_bounce(t * 2 - d, 0, c, d) * 0.5 + c * 0.5 + b

#Animation
class Animation(threading.Thread):
    STATE_STARTED = "started"
    STATE_STOPPED = "stopped"
    STATE_READY = "ready"
    STATE_DEFAULT = "default"

    def __init__(self, sprite):
        threading.Thread.__init__(self)
        self.sprite = sprite
        self.__animation = None
        self.__animation_finish = None
        self.state = self.STATE_DEFAULT
        self.time = 0
        self.clock = pygame.time.Clock()
        self.duration = 0
        self.__attrs = dict()
        self.delay = 0

    def animate(self, attrs, duration=1000, easing=None, delay=0, callback=None):
        """
        General design for animation
        support the following attributes in sprites:
        x, y, width, height, color[c1, c2, c3]
        """

        if easing:
            self.easing = easing
        else:
            self.easing = Easing.ease_linear

        self.callback = callback
        self.duration = duration
        self.delay = delay
        self.attrs = attrs
        self.__animation = self._animation_attrs
        self.__animation_finish = self._animate_attrs_finish
        self.state = self.STATE_READY

    def __init_attrs(self, attrs):
        """
        supporting:
        x, y, width, height, color[c1, c2, c3]
        """
        self.__attrs = dict()
        for key, val in attrs.iteritems():
            current_value = getattr(self.sprite.rect, key)
            self.__attrs[key] = (current_value, val, val - current_value)

            #raise Exception("Animation: {} property is not supported.".format(key))

    def _animation_attrs(self):
        self.__init_attrs(self.attrs)
        self.clock.tick()
        self.time = 0
        while self.time <= self.duration:
            self.clock.tick()
            self.time += self.clock.get_time()
            for key, val in self.__attrs.iteritems():
                if val[2] == 0:
                    continue
                new_val = self.easing(float(self.time), float(val[0]), float(val[2]),
                                      float(self.duration))
                setattr(self.sprite.rect, key, new_val)

    def _animate_attrs_finish(self):
        for key, val in self.__attrs.iteritems():
            try:
                setattr(self.sprite.rect, key, val[1])
            except TypeError:
                pass

    def run(self):
        self.state = self.STATE_STARTED

        try:
            if self.delay:
                pygame.time.delay(self.delay)
            self.__animation()
        except ValueError:
            pass
        finally:
            if self.__animation_finish:
                self.__animation_finish()

        self.state = self.STATE_STOPPED
        if self.callback:
            self.callback.execute()


class AnimationCallback(object):
    def execute(self):
        pass

class AnimatinoSequencialCallback(AnimationCallback):
    def __init__(self, animation):
        self.animation = animation

    def execute(self):
        self.animation.start()
