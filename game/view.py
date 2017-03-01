__author__ = 'Lemon'

from listener import *
from event import *
from model import *
from animation import *
from utility import *
import pygame
import random
from pygame.locals import *
import os
import pickle

#class AnimatedSprite
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, width=0, height=0, color=(0, 0, 0)):
        pygame.sprite.Sprite.__init__(self)
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([width, height])
        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.width = width
        self.rect.height = height
        self.color = color
        self.animations = []

    #add the animation
    def add_animation(self, animation):
        self.animations.append(animation)

    #emputy the animations
    def clear_animation(self):
        self.animations = []

    #start animation
    def start_animation(self):
        for i in range(1, len(self.animations)):
            pre = self.animations[i - 1]
            current = self.animations[i]
            pre.callback = AnimatinoSequencialCallback(current)

        if self.animations:
            self.animations[0].start()

        self.clear_animation()

    def update(self, *args):
        self.image.fill(self.color)
        # print text on the button, text
        self.rect.center = self.image.get_width() / 2 + self.rect.x, self.image.get_height() / 2 + self.rect.y
        self.rect.width = max(self.rect.width, 3)
        self.rect.height = max(self.rect.height, 3)
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))


#Abstract View
class AbstractView(Listener, AnimatedSprite):
    def __init__(self, event_manager, parent_view, width=0, height=0, color=(0, 0, 0)):
        Listener.__init__(self, event_manager)
        AnimatedSprite.__init__(self, width, height, color)
        self.parent_view = parent_view
        self.views = []

    #remove from view by kill() method
    def remove_from_view(self):
        for v in self.views:
            v.kill()

        self.kill()


#EmptyView class
class EmptyView(Listener):
    def __init__(self, event_manager, width=600, height=900):
        Listener.__init__(self, event_manager)
        self.views = pygame.sprite.LayeredUpdates()
        self.width = width
        self.height = height
        self.init_graphics()

    #add view
    def add_view(self, view):
        self.views.add(view)
        view.super_view = self

    #remove view
    def remove_view(self, view):
        self.views.remove(view)

    #listen for events
    def notify(self, ev):
        if isinstance(ev, TickEvent):
            self.update_graphics()
            # limit the redraw speed to 30 frames per second
            self.clock.tick(50)

    #set size of screen and the name of game
    def init_graphics(self):
        pygame.display.set_caption('Space war')
        self.screen = pygame.display.set_mode([self.width, self.height], 0, 32)
        self.clock = pygame.time.Clock()
        self.small_font = pygame.font.Font(None, 40)

    #draw the screen
    def update_graphics(self):
        # clear display
        self.screen.fill((0, 0, 0))

        self.views.update()
        self.views.draw(self.screen)

        # flip the display to show whatever we drew
        pygame.display.flip()


#main view
class MainView(Listener):
    STATE_INITIAL = "INITIAL"
    STATE_PLAYING = "PLAYING"
    STATE_GAME_OVER = "END"

    def __init__(self, event_manager, width=600, height=900):
        super(MainView, self).__init__(event_manager)
        self.views = pygame.sprite.LayeredUpdates()
        self.width = width
        self.height = height
        self.game_state = self.STATE_INITIAL
        self.init_graphics()
        self.init_components()

    #add view to main view
    def add_view(self, view, layer=0):
        if layer:
            view._layer = layer
        self.views.add(view)
        view.parent_view = self

    #change the layer
    def change_layer(self, source, layer):
        self.views.change_layer(source, layer)

    #delete view
    def remove_view(self, view):
        self.views.remove(view)

    #listen for events
    def notify(self, ev):
        if isinstance(ev, TickEvent):
            self.update()
            # limit the redraw speed to 30 frames per second
            self.clock.tick(50)
        elif isinstance(ev, GameWelcomeEvent):
            self.game_welcome()
        elif isinstance(ev, GameStartedEvent):
            self.game_start()
        elif isinstance(ev, GameOverEvent):
            self.game_over()
        elif isinstance(ev, GamePlayerShipChangedEvent):
            self.player_ship_name = ev.ship_name
        elif isinstance(ev, KeyboardEvent):
            # for test only
            if ev.ev.type == pygame.KEYDOWN:
                if ev.ev.key == pygame.K_5:
                    self.notify_all(GameWelcomeEvent())
                if ev.ev.key == pygame.K_6:
                    self.notify_all(GameStartedEvent())
                if ev.ev.key == pygame.K_7:
                    self.notify_all(GameOverEvent())
        elif isinstance(ev, GameDifficultyChangedEvent):
            self.set_difficulty(ev.difficulty)

    #set the level of game if player do not select level, the level would be set as normal by system
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        if difficulty == "HARD":
            self.player_life_max = 2
        elif difficulty == "NORMAL":
            self.player_life_max = 3
        else:
            self.player_life_max = 9

    #set size of screen and the name of game
    def init_graphics(self):
        pygame.display.set_caption('Space War')
        self.screen = pygame.display.set_mode([self.width, self.height], 0, 32)
        self.clock = pygame.time.Clock()

    #init components such as player life and player speed
    def init_components(self):
        self.background = GameBackground(self.event_manager, self)
        self.add_view(self.background)

        self.player_speed_y_max = self.player_speed_x_max = 7
        self.player_life_max = 3
        self.player_life = self.player_life_max
        self.difficulty = "NORMAL"
        self.player_ship_name = ComponentFactory.PLAYER_BLUE_1
        self.player = None
        self.life_view = None
        self.score_view = None
        self.game_over_view = None
        self.welcome_view = None

        # init level
        self.level_view = LevelView(self.event_manager, self)
        self.add_view(self.level_view)

        self.notify_all(GameWelcomeEvent())

    #check collision is player touch the bullet or enemies they would be deleted from their groups
    def __test_collision(self):
        if self.game_state != self.STATE_PLAYING:
            return

        bullets_player = pygame.sprite.Group()

        bullets_enemy = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        for v in self.views:
            if isinstance(v, Bullet):
                if isinstance(v.source, Player):
                    bullets_player.add(v)
                else:
                    bullets_enemy.add(v)
            elif isinstance(v, Enemy):
                enemies.add(v)

        hit_player = pygame.sprite.spritecollide(self.player, enemies, False)
        if hit_player:
            self.__handle_player_hit()
            return

        hit_player = pygame.sprite.spritecollide(self.player, bullets_enemy, False)
        if hit_player:
            for bullet in hit_player:
                bullet.remove(bullet.groups())
            self.__handle_player_hit()
            return

        for b in bullets_player:
            hit_by_player = pygame.sprite.spritecollide(b, enemies, False)
            if hit_by_player:
                b.remove(b.groups())
                for enemy in hit_by_player:
                    enemy.hit()

    # call the functions if player is hit and remove it from view
    def __clear_views(self):
        if self.player:
            self.player.remove_from_view()
        if self.life_view:
            self.life_view.remove_from_view()
        if self.score_view:
            self.score_view.remove_from_view()
        if self.game_over_view:
            self.game_over_view.remove_from_view()
        if self.welcome_view:
            self.welcome_view.remove_from_view()

    #handle player is hit, if player is hit life -1 until dead
    def __handle_player_hit(self):
        self.player.hit()
        if not self.player.is_dead:
            return

        self.player_life -= 1
        if self.player_life < 0:
            self.notify_all(GameOverEvent())
            pass
        else:
            self.notify_all(PlayerLifeChangedEvent(self.player_life))

    #replay the game
    def __test_replay(self):
        if self.game_state != self.STATE_PLAYING:
            return

        if self.player.is_dead:
            # replay
            self.player = ComponentFactory.create_player_ship(self.event_manager, self, self.player_ship_name)
            self.add_view(self.player)

    #update the views
    def update(self):
        self.__test_collision()
        self.__test_replay()

        # clear display
        self.screen.fill((0, 0, 0))
        self.views.update()
        self.views.draw(self.screen)

        # flip the display to show whatever we drew
        pygame.display.flip()

    #back to game welcome background to play the music and clear the views
    def game_welcome(self):
        self.__clear_views()
        self.game_state = self.STATE_INITIAL
        self.welcome_view = GameWelcomeView(self.event_manager, self)
        self.add_view(self.welcome_view)
        Sound.stop_game_over()
        Sound.play_background()

    #start the game and make new setting
    def game_start(self):
        self.__clear_views()
        self.player_life = self.player_life_max
        self.player = ComponentFactory.create_player_ship(self.event_manager, self, self.player_ship_name)
        self.player.speed_y_max = self.player_speed_y_max
        self.player.speed_x_max = self.player_speed_x_max
        self.add_view(self.player)

        self.enemy = ComponentFactory.create_enemy_ship(self.event_manager, self, ComponentFactory.ENEMY_BLACK_5)
        self.add_view(self.enemy)

        self.life_view = PlayerLifeView(self.event_manager, self, self.player_life, self.player_ship_name)
        self.add_view(self.life_view)

        self.score_view = PlayerScoreView(self.event_manager, self)
        self.add_view(self.score_view)

        self.game_state = self.STATE_PLAYING
        # your code goes here.
        # LEVEL DESIGN GOES HERE
        if Sound.is_game_over_playing():
            Sound.stop_game_over()
            Sound.play_background()

    #jump to the game over view and play the music of game over
    def game_over(self):
        score = 0
        if self.score_view:
            score = self.score_view.score
        self.__clear_views()
        self.game_state = self.STATE_GAME_OVER
        # init the game over view
        if score:
            self.score_view = PlayerScoreView(self.event_manager, self)
            self.score_view.add_score(score)
            self.add_view(self.score_view)

        self.game_over_view = GameOverView(self.event_manager, self)
        self.add_view(self.game_over_view)
        Sound.stop_background()
        Sound.play_game_over()


#class game background
class GameBackground(AbstractView):
    def __init__(self, event_manager, parent_view, width=600, height=900, color=(90, 90, 90)):
        AbstractView.__init__(self, event_manager, parent_view, width, height, color)
        self.color = color
        self._layer = 1
        self.__init_background()

    def __init_background(self):
        self.image = ComponentFactory.load_image('image', 'background2.jpg')
        width = self.image.get_width()
        height = self.image.get_height()
        self.background = pygame.Surface([width, height * 2])
        self.background.blit(self.image, [0, 0])
        self.background.blit(self.image, [0, height])
        self.index = height
        self.speed = 0.5

    #listen for events
    def notify(self, ev):
        if isinstance(ev, TickEvent):
            self.__update_background()
        elif isinstance(ev, GameDifficultyChangedEvent):
            self.set_difficulty(ev.difficulty)

    #set the level of game if not select it would be set by system
    def set_difficulty(self, difficulty):
        if difficulty == "HARD":
            self.speed = 2
        elif difficulty == "NORMAL":
            self.speed = 1
        else:
            self.speed = 0.5

    #update background
    def __update_background(self):
        self.index += self.speed
        if self.index >= self.image.get_height() * 2:
            self.index = self.image.get_height()

    #draw the background
    def update(self, *args):
        self.image.blit(self.background, [0, int(self.index - self.image.get_height() * 2)])


#player score view
class PlayerScoreView(AbstractView):
    def __init__(self, event_manager, parent_view, score=0, width=0, height=0, color=(90, 90, 90)):
        AbstractView.__init__(self, event_manager, parent_view, width, height, color)
        self.color = color
        self._layer = 10
        self.score = score
        self.views = []
        self.base_position = [550, 100]
        self.index = 0
        self.__update_score_view(self.score)

    #add the score if user hit enemy or enemy down
    def add_score(self, score):
        self.score += score
        self.__update_score_view(self.score)

    #listen for events
    def notify(self, ev):
        if isinstance(ev, PlayerScoreChangedEvent):
            self.add_score(ev.score)

    def update(self, *args):
        pass

    #add the score if user hit enemy or enemy down
    def __update_score_view(self, score):
        for d in self.views:
            d.remove(d.groups())

        icons = ComponentFactory.create_number_image(score)
        padding = 0
        for i in range(len(icons)):
            icon = icons[i]
            width, height = icon.get_width(), icon.get_height()
            digit = IconButton(self.event_manager, self.parent_view, "", icons[i], width, height)
            padding += width + 2
            digit.rect.left = padding
            digit.rect.top = 20
            self.parent_view.add_view(digit)
            self.views.append(digit)


#player life view
class PlayerLifeView(AbstractView):
    INITIAL_POSITION = 30, 850

    def __init__(self, event_manager, parent_view, life, name=None, width=0, height=0, color=(90, 90, 90)):
        AbstractView.__init__(self, event_manager, parent_view, width, height, color)
        self.color = color
        self._layer = 10
        if name:
            icon = ComponentFactory.load_image('image', 'PNG', name + ".png")
        else:
            icon = ComponentFactory.load_image('image', 'PNG', 'playerShip3_blue.png')

        icon_width, icon_height = icon.get_width(), icon.get_height()
        icon = pygame.transform.smoothscale(icon, (icon_width / 2, icon_height / 2))
        icon_width, icon_height = icon.get_width(), icon.get_height()
        self.life_icon_view = IconButton(event_manager, parent_view, "", icon, icon_width, icon_height)
        self.life_icon_view.rect.centerx = self.INITIAL_POSITION[0]
        self.life_icon_view.rect.centery = self.INITIAL_POSITION[1]
        self.parent_view.add_view(self.life_icon_view)

        icon = ComponentFactory.load_image('image', 'PNG', 'UI', 'numeralX.png')
        icon_width, icon_height = icon.get_width(), icon.get_height()
        self.cross_icon_view = IconButton(event_manager, parent_view, "", icon, icon_width, icon_height)
        self.cross_icon_view.rect.centerx = self.INITIAL_POSITION[0] + 30
        self.cross_icon_view.rect.centery = self.INITIAL_POSITION[1]
        self.parent_view.add_view(self.cross_icon_view)

        icon = ComponentFactory.load_image('image', 'PNG', 'UI', 'numeral' + str(life) + '.png')
        icon_width, icon_height = icon.get_width(), icon.get_height()
        self.number_icon_view = IconButton(event_manager, parent_view, "", icon, icon_width, icon_height)
        self.number_icon_view.rect.centerx = self.INITIAL_POSITION[0] + 60
        self.number_icon_view.rect.centery = self.INITIAL_POSITION[1]
        self.parent_view.add_view(self.number_icon_view)

    #set life such position or image
    def set_life(self, n):
        self.number_icon_view.kill()
        icon = ComponentFactory.load_image('image', 'PNG', 'UI', 'numeral' + str(n) + '.png')
        icon_width, icon_height = icon.get_width(), icon.get_height()
        self.number_icon_view = IconButton(self.event_manager, self.parent_view, "", icon, icon_width, icon_height)
        self.number_icon_view.rect.centerx = self.INITIAL_POSITION[0] + 60
        self.number_icon_view.rect.centery = self.INITIAL_POSITION[1]
        self.parent_view.add_view(self.number_icon_view)

    #listen for events
    def notify(self, ev):
        if isinstance(ev, PlayerLifeChangedEvent):
            self.set_life(ev.life)

    def update(self, *args):
        pass

    #if player info changed remove or kill life from groups
    def remove_from_view(self):
        self.life_icon_view.kill()
        self.cross_icon_view.kill()
        self.number_icon_view.kill()
        self.kill()


#game over view
class GameOverView(AbstractView):
    def __init__(self, event_manager, parent_view, width=0, height=0, color=(90, 90, 90)):
        AbstractView.__init__(self, event_manager, parent_view, width, height, color)
        self.color = color
        self._layer = 0
        self.__init_components()

    def update(self, *args):
        pass

    #listen for events
    def notify(self, ev):
        if isinstance(ev, ButtonClickedEvent):
            self.__handle_button_event(ev)

    #handle button events
    def __handle_button_event(self, ev):
        name = ev.source.name

        if name == "REPLAY_GameOverView":
            self.notify_all(GameStartedEvent())
        if name == "BACK_GameOverView":
            self.notify_all(GameWelcomeEvent())
        if name == "QUIT_GameOverView":
            self.notify_all(QuitEvent())

    def __init_components(self):
        self.views = []

        names = ["REPLAY_GameOverView", "BACK_GameOverView", "QUIT_GameOverView"]
        filenames = ["Replay", "Back", "Exit"]
        for i in range(3):
            filename = filenames[i] + "0.png"
            icon = ComponentFactory.load_image('image', 'PNG', 'UI', filename)
            width, height = icon.get_width(), icon.get_height()
            button = IconButton(self.event_manager, self.parent_view, names[i], icon, width, height)

            for k in range(1, 10):
                filename = filenames[i] + str(k) + ".png"
                icon = ComponentFactory.load_image('image', 'PNG', 'UI', filename)
                button.images.append(icon)

            button.image.set_alpha(200)
            button.rect.centerx = 300
            button.rect.centery = 700 + i * 70
            self.parent_view.add_view(button)
            self.views.append(button)

        icon = ComponentFactory.load_image('image', 'gameover.png')
        width, height = icon.get_width(), icon.get_height()
        button = IconButton(self.event_manager, self.parent_view, "", icon, width, height)
        button.rect.centerx = 300
        button.rect.y = 100
        self.parent_view.add_view(button)
        self.views.append(button)


#level view
class LevelView(AbstractView):
    def __init__(self, event_manager, parent_view):
        AbstractView.__init__(self, event_manager, parent_view, 1, 1, [0, 0, 0])
        self.color = color
        self._layer = 0
        self.is_active = False
        self.total_tick_counter = 0
        self.current_tick_counter = 0
        self.route_index = 0
        # difficulty settings
        self.set_difficulty("NORMAL")
        self.__init_components()

    def __init_components(self):
        try:
            with open('route_file.prg', 'rb') as route_file:
                self.route_manager = pickle.load(route_file)
        except:
            self.route_manager = RouteManager()

    #listen for events
    def notify(self, ev):
        if isinstance(ev, GameStartedEvent):
            self.__handle_game_start()
        elif isinstance(ev, GameOverEvent):
            self.__handle_game_over()
        elif isinstance(ev, TickEvent):
            self.__handle_tick()
        elif isinstance(ev, GameDifficultyChangedEvent):
            self.set_difficulty(ev.difficulty)

    # to init the difficulty
    # canshu
    def set_difficulty(self, difficulty):
        if difficulty == "HARD":
            self.interval = 150
            self.step = 6
            self.bullet_speed = 1.1
            self.fleet_num = 4
            self.bullet_number = 3
            self.hp = 2
        elif difficulty == "NORMAL":
            self.interval = 200
            self.step = 5
            self.bullet_speed = 1
            self.fleet_num = 2
            self.bullet_number = 2
            self.hp = 1
        else:
            self.interval = 300
            self.step = 3
            self.bullet_speed = 0.8
            self.fleet_num = 1
            self.bullet_number = 1
            self.hp = 1

    def update(self, *args):
        pass

    #handle game over if player down there would be changed to true
    def __handle_game_over(self):
        self.is_active = False

    #handle game start if player down there would be changed to true
    def __handle_game_start(self):
        self.is_active = True
        self.total_tick_counter = 0
        self.route_index = 0

    #handle tick 50
    def __handle_tick(self):
        if not self.is_active:
            return

        self.total_tick_counter += 1
        self.current_tick_counter += 1

        if self.current_tick_counter >= self.interval:
            self.current_tick_counter = 0
            self.release_fleet()

    #sent the fleet out
    def release_fleet(self):
        self.route_index += 1
        self.route_index %= len(self.route_manager.routes)
        route = self.route_manager.get_route(self.route_index)
        route.step = self.step
        fleet = Fleet(self.event_manager, self.parent_view, route.copy())
        fleet.num = self.fleet_num
        fleet.bullet_speed = self.bullet_speed
        fleet.bullet_number = self.bullet_number
        fleet.hp = self.hp
        self.parent_view.add_view(fleet)
        fleet.start()


#fleet
class Fleet(AbstractView):
    def __init__(self, event_manager, parent_view, route):
        AbstractView.__init__(self, event_manager, parent_view, 1, 1, [0, 0, 0])
        self.route = route
        self._layer = 0
        self.num = 1
        self.interval = 25
        self.bullet_speed = 1
        #self.ships = pygame.sprite.Group()
        self.is_active = False
        self.tick_counter = 0
        self.num_count = 0
        self.bullet_number = 1
        self.hp = 1

    #game is start
    def start(self):
        self.is_active = True

    def update(self, *args):
        pass

    #listen for events
    def notify(self, ev):
        if isinstance(ev, TickEvent):
            self.__handle_tick()

    #handle tick
    def __handle_tick(self):
        if not self.is_active:
            return

        if self.num_count >= self.num:
            return

        self.tick_counter += 1
        self.tick_counter %= self.interval
        if self.tick_counter == 1:
            self.release_ship()
            self.num_count += 1

    #set the release ships
    def release_ship(self):
        name = ComponentFactory.ENEMY_SHIPS[random.randrange(len(ComponentFactory.ENEMY_SHIPS))]
        ship = ComponentFactory.create_enemy_ship(self.event_manager, self.parent_view, name)
        ship.bullet_speed = self.bullet_speed
        ship.hp = self.hp
        ship.route = self.__init_route()
        self.parent_view.add_view(ship)
        #self.ships.add(ship)

    #the route of ships
    def __init_route(self):
        route = self.route.copy()

        interval = route.length() / route.step / (self.bullet_number + 1)
        bullet_count = 0
        counter = 0
        state = route.get_next()
        while state and bullet_count <= self.bullet_number:
            counter += 1
            counter %= interval
            if counter == interval - 1:
                state[2] = 1
                bullet_count += 1
            state = route.get_next()

        route.reset()
        return route


#gamewelcomeview
class GameWelcomeView(AbstractView):
    MENU_MAIN = ["LAUNCH", "SETTINGS", "HELP", "EXIT"]
    MENU_SETTINGS_NAMES = ["EASY", "NORMAL", "HARD", "BACK_SETTINGS"]

    def __init__(self, event_manager, parent_view, width=600, height=900, color=(90, 90, 90)):
        AbstractView.__init__(self, event_manager, parent_view, width, height, color)
        self.color = color
        self._layer = 0
        self.__init_components()

    def __init_components(self):
        m = self.event_manager
        v = self.parent_view
        button_color = [50, 50, 50]
        self.views = []

        self.group_main = []
        names = self.MENU_MAIN
        filenames = ["Launch", "Settings", "Help", "Exit"]
        for i in range(len(names)):
            filename = filenames[i] + "0.png"
            icon = ComponentFactory.load_image('image', 'PNG', 'UI', filename)
            width, height = icon.get_width(), icon.get_height()
            button = IconButton(self.event_manager, self.parent_view, names[i], icon, width, height)

            for k in range(1, 10):
                filename = filenames[i] + str(k) + ".png"
                icon = ComponentFactory.load_image('image', 'PNG', 'UI', filename)
                button.images.append(icon)

            #button = Button(m, v, names[i], names[i], width=150, color=button_color)
            button.image.set_alpha(200)
            button.initial_position = 300, 600 + i * 70
            button.rect.centerx = 300
            button.rect.top = 600 + i * 70
            self.parent_view.add_view(button)
            self.group_main.append(button)
            self.views.append(button)

        self.group_settings_menu = []
        names = self.MENU_SETTINGS_NAMES
        filenames = ["Easy", "Normal", "Hard", "Back"]
        for i in range(len(names)):
            filename = filenames[i] + "0.png"
            icon = ComponentFactory.load_image('image', 'PNG', 'UI', filename)
            width, height = icon.get_width(), icon.get_height()
            button = IconButton(self.event_manager, self.parent_view, names[i], icon, width, height)

            for k in range(1, 10):
                filename = filenames[i] + str(k) + ".png"
                icon = ComponentFactory.load_image('image', 'PNG', 'UI', filename)
                button.images.append(icon)

            button.image.set_alpha(200)
            button.rect.left = 700
            button.rect.top = 600 + i * 70
            button.initial_position = 300, 600 + i * 70
            self.parent_view.add_view(button)
            self.group_settings_menu.append(button)
            self.views.append(button)

        self.group_settings_ships = []
        for i in range(len(ComponentFactory.PLAYER_SHIPS)):
            name = ComponentFactory.PLAYER_SHIPS[i]
            filename = name + ".png"
            icon = ComponentFactory.load_image('image', 'PNG', filename)
            width, height = ComponentFactory.get_ship_size(name)
            button = ShipSelectButton(self.event_manager, self, name, icon, width, height)
            button.initial_position = 130 * (i % 3) + 160, 130 * (i / 3) + 50
            button.rect.x, button.rect.y = button.initial_position[0] + 600, button.initial_position[1]
            self.parent_view.add_view(button)
            self.group_settings_ships.append(button)
            self.views.append(button)

        self.update_hightlight()

        self.group_help = []
        filename = "help.png"
        icon = ComponentFactory.load_image('image', 'PNG', 'UI', filename)
        width, height = icon.get_width(), icon.get_height()
        button = IconButton(self.event_manager, self.parent_view, "HELP", icon, width, height)
        button.initial_position = 900, 100
        button.rect.centerx, button.rect.y = button.initial_position[0], button.initial_position[1]
        self.parent_view.add_view(button)
        self.group_help.append(button)
        self.views.append(button)

        filename = "Back0.png"
        icon = ComponentFactory.load_image('image', 'PNG', 'UI', filename)
        width, height = icon.get_width(), icon.get_height()
        button = IconButton(self.event_manager, self.parent_view, "BACK_HELP", icon, width, height)
        for k in range(1, 10):
            filename = "Back" + str(k) + ".png"
            icon = ComponentFactory.load_image('image', 'PNG', 'UI', filename)
            button.images.append(icon)

        button.image.set_alpha(200)
        button.rect.left = 700
        button.rect.top = 810
        button.initial_position = 300, 810
        self.parent_view.add_view(button)
        self.group_help.append(button)
        self.views.append(button)

    #listem for events
    def notify(self, ev):
        if isinstance(ev, ButtonClickedEvent):
            self.__handle_button_event(ev)

    #handle button events
    def __handle_button_event(self, ev):
        source = ev.source
        # main menu
        if source.name == "LAUNCH":
            self.leave_menu_main()
            self.notify_all(GameStartedEvent())
        elif source.name == "SETTINGS":
            self.enter_settings()
        elif source.name == "HELP":
            self.enter_help()
        elif source.name == "BACK_HELP":
            self.leave_help()
            self.enter_menu_main()
        elif source.name == "EXIT":
            self.leave_menu_main()
            self.notify_all(QuitEvent())

        # settings
        if source.name in self.MENU_SETTINGS_NAMES:
            if source.name in ["EASY", "NORMAL", "HARD"]:
                self.notify_all(GameDifficultyChangedEvent(source.name))
                self.update_hightlight()
            if source.name == "BACK_SETTINGS":
                self.leave_menu_settings()
                self.enter_menu_main()

        if source.name in ComponentFactory.PLAYER_SHIPS:
            self.notify_all(GamePlayerShipChangedEvent(source.name))
            self.update_hightlight()

    #update hight light
    def update_hightlight(self):
        self.highlight_names = [self.parent_view.difficulty, self.parent_view.player_ship_name]
        for item in self.group_settings_menu:
            if item.name in self.highlight_names:
                item.selected = True
            else:
                item.selected = False
        for item in self.group_settings_ships:
            if item.name in self.highlight_names:
                item.selected = True
            else:
                item.selected = False

    #fill the image
    def update(self, *args):
        self.image.fill(self.color)

    #animation of the main menu
    def enter_menu_main(self):
        delay_before = 300
        group = self.group_main
        for i in range(len(group)):
            delay = i * 100 + delay_before
            go_x = group[i].initial_position[0]
            animation = Animation(group[i])
            animation.animate({"centerx": go_x}, duration=300, easing=Easing.ease_in_out_back, delay=delay)
            animation.start()

    #animation of the main menu
    def leave_menu_main(self):
        group = self.group_main
        for i in range(len(group)):
            delay = i * 100
            animation = Animation(group[i])
            animation.animate({"right": -10}, duration=300, easing=Easing.ease_in_out_back, delay=delay)
            animation.start()

    #animation of the setting menu
    def enter_settings(self):
        self.leave_menu_main()

        delay_before = 400
        group = self.group_settings_menu
        for i in range(len(group)):
            delay = i * 100 + delay_before
            animation = Animation(group[i])
            go_x = group[i].initial_position[0]
            animation.animate({"centerx": go_x}, duration=400, easing=Easing.ease_in_out_back, delay=delay)
            animation.start()

        group = self.group_settings_ships
        for i in range(len(group)):
            delay = i * 20 + delay_before
            animation = Animation(group[i])
            go_x = group[i].initial_position[0]
            animation.animate({"centerx": go_x}, duration=400, easing=Easing.ease_in_out_back, delay=delay)
            animation.start()

    #animation of the setting menu
    def leave_menu_settings(self):
        group = self.group_settings_menu
        for i in range(len(group)):
            delay = i * 100
            animation = Animation(group[i])
            animation.animate({"left": 610}, duration=300, easing=Easing.ease_in_out_back, delay=delay)
            animation.start()

        group = self.group_settings_ships
        for i in range(len(group)):
            delay = i * 20
            animation = Animation(group[i])
            animation.animate({"left": 610}, duration=300, easing=Easing.ease_in_out_back, delay=delay)
            animation.start()

    #animation of the help menu
    def enter_help(self):
        self.leave_menu_main()

        delay_before = 400
        group = self.group_help
        for i in range(len(group)):
            delay = i * 100 + delay_before
            animation = Animation(group[i])
            animation.animate({"centerx": 300}, duration=400, easing=Easing.ease_in_out_back, delay=delay)
            animation.start()

    #animation of the help menu
    def leave_help(self):
        group = self.group_help
        for i in range(len(group)):
            delay = i * 100
            animation = Animation(group[i])
            animation.animate({"left": 610}, duration=300, easing=Easing.ease_in_out_back, delay=delay)
            animation.start()

#random background view
class RandomBackgroundView(AbstractView):
    def __init__(self, event_manager, parent_view, width=0, height=0, color=(0, 0, 0)):
        AbstractView.__init__(self, event_manager, parent_view, width, height, color)
        self.init_color()

    def notify(self, event):
        pass

    def init_color(self):
        self.color = [125, 125, 125]
        self.signs = [1, 1, 1]
        self.steps = [3, 6, 9]

    def update(self, *args):
        for i in range(3):
            c = self.color[i]
            step = self.steps[i]
            sign = self.signs[i]
            r = random.randint(0, step)
            if c + sign * step > 255:
                self.color[i] = 255
                self.signs[i] = -1
            elif c + sign * step < 0:
                self.color[i] = 0
                self.signs[i] = 1
            else:
                self.color[i] += r * sign
        self.image.fill(self.color)

#view for text
class TextView(AbstractView):
    def __init__(self, event_manager, parent_view, width=0, height=0, color=(100, 100, 100)):
        AbstractView.__init__(self, event_manager, parent_view, width, height, color)
        self.init_color()
        self.rect.x = 100
        self.rect.y = 200
        self.font = pygame.font.Font(None, 30)
        self.text = ""

    #listen for events
    def notify(self, ev):
        if isinstance(ev, TextUpdateEvent):
            self.__update_text(ev.text)

    #set color
    def init_color(self):
        self.color = [170, 200, 0]
        self.signs = [1, 1, 1]
        self.steps = [3, 6, 9]

    #text for update
    def __update_text(self, text):
        self.text = text

    #background for update
    def __update_background(self):
        text = self.font.render("text", True, (0, 0, 0))
        height = len(self.text.split("\n")) * text.get_height()
        self.rect.height = height
        self.image = pygame.Surface([self.rect.width, self.rect.height])
        self.image.fill(self.color)

    def update(self, *args):
        self.__update_background()

        lines = self.text.split("\n")

        for i in range(len(lines)):
            line = lines[i]
            if i == len(lines) - 1:
                line += "_"
            text = self.font.render(line, True, (0, 0, 0))
            self.image.blit(text, [0, i * text.get_height()])

#view for number input
class NumberInputView(TextView):
    LEGAL_KEYS = [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]

    def __init__(self, event_manager, parent_view, width=0, height=0, color=(100, 100, 100)):
        TextView.__init__(self, event_manager, parent_view, width, height, color)
        self.init_color()
        self.font = pygame.font.Font(None, 30)
        self.number = 0

    #listen for events
    def notify(self, ev):
        if isinstance(ev, KeyboardEvent):
            self.__handle_keyboard_event(ev)

    #handle keyboard events
    def __handle_keyboard_event(self, ev):
        event = ev.ev
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if abs(self.number) < 1:
                    self.number = 0
                else:
                    self.number /= 10
                self.notify_all(NumberChangedEvent(self.number))
            elif event.key in self.LEGAL_KEYS:
                self.number = self.number * 10 + int(chr(event.key))
                self.notify_all(NumberChangedEvent(self.number))
            elif event.key == pygame.K_EQUALS:
                self.number += 1
                self.notify_all(NumberChangedEvent(self.number))
            elif event.key == pygame.K_MINUS:
                self.number -= 1
                self.notify_all(NumberChangedEvent(self.number))

    #text for update
    def __update_text(self, text):
        self.text = text

    #background for update
    def __update_background(self):
        self.image = pygame.Surface([self.rect.width, self.rect.height])
        self.image.fill(self.color)

    def update(self, *args):
        self.__update_background()

        text = self.font.render(str(self.number), True, (0, 0, 0))
        self.image.blit(text, [0, 0])


#button
class Button(AbstractView):
    # model controller view
    def __init__(self, event_manager, parent_view, text="", name="", width=91, height=54, color=(100, 100, 100)):
        AbstractView.__init__(self, event_manager, parent_view, width, height, color)
        self.color = color
        self.color_initial = self.color
        self.text = text
        self.name = name
        self._layer = 999
        self.on_hover = False
        self.color_hover = [20, 20, 200]
        self.selected = False

    #listen for events
    def notify(self, ev):
        if not self.alive():
            return
        if isinstance(ev, MouseClickEvent):
            # logic layer
            self._handle_click_event(ev)
        if isinstance(ev, TickEvent):
            self._handle_hover_event()

    def update(self, *args):
        if self.on_hover or self.selected:
            self.color = self.color_hover
            self.on_hover = False
        else:
            self.color = self.color_initial

        self.image.fill(self.color)
        # print text on the button, text
        text = self.font.render(self.text, True, (255, 255, 255))
        text_x = self.image.get_width() / 2 - text.get_width() / 2
        text_y = self.image.get_height() / 2 - text.get_height() / 2
        self.image.blit(text, [text_x, text_y])

    #handle click even
    def _handle_click_event(self, ev):
        # try to see is I was clicked
        if self.rect.collidepoint(ev.pos):
            self.notify_all(ButtonClickedEvent(self))

    #handle hover event
    def _handle_hover_event(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.on_hover = True


#view for icon button
class IconButton(Button):
    def __init__(self, event_manager, parent_view, name="", icon=None, width=91, height=54):
        Button.__init__(self, event_manager, parent_view, "", name, width, height)
        self.icon = icon
        self.images = [icon]
        self.image_index = 0
        self.frame_speed = 2
        self.frame_counter = 0
        self.loop = False

    def update(self, *args):
        if self.selected:
            icon = self.images[-1]
            self.image = icon.copy()
            return

        if self.on_hover:
            #deal with hover
            if len(self.images) >= 2:
                self.frame_counter += 1
                self.frame_counter %= self.frame_speed
                if self.frame_counter == 1:
                    self.image_index += 1

                if self.image_index >= len(self.images) - 1:
                    if self.loop:
                        self.image_index = 1
                    else:
                        self.image_index = len(self.images) - 1
        else:
            self.image_index = 0

        icon = self.images[self.image_index]
        self.image = icon.copy()

        self.on_hover = False


#ship select button
class ShipSelectButton(IconButton):
    def __init__(self, event_manager, parent_view, name="", icon=None, width=91, height=54):
        Button.__init__(self, event_manager, parent_view, "", name, width, height)
        self.icon = icon

    def update(self, *args):
        self.image = self.icon.copy()

        if self.on_hover or self.selected:
            pygame.draw.rect(self.image, self.color_hover, [0, 0, self.image.get_width(), self.image.get_height()], 10)
            self.on_hover = False


#bullet
class Bullet(AbstractView):
    def __init__(self, manager, parent_view, vector, source, image=None, width=15, height=15, color=(0, 255, 255)):
        AbstractView.__init__(self, manager, parent_view, width, height, color)
        self.color = color
        self.route = None
        self.vector = vector
        self._layer = 2
        self.source = source
        self.target = None
        if image:
            self.image = image
        else:
            if isinstance(self.source, Player):
                self.image = ComponentFactory.load_image('image', 'PNG', 'Lasers', 'laserBlue01.png')
            else:
                self.image = ComponentFactory.load_image('image', 'bullet0.png')
        self.rect = self.image.get_rect()
        self.position = [self.rect.centerx, self.rect.centery]

    #set bullet position
    def set_position(self, x, y):
        self.rect.centerx, self.rect.centery = x, y
        self.position = [self.rect.centerx, self.rect.centery]

    def notify(self, ev):
        pass

    #if bullet is out of bonus of the screen it would be remove from groups
    def __test_destroy(self):
        if self.rect.centerx < 0 - 300 or self.rect.centerx > 600 + 300:
            self.remove(self.groups())
            return True
        if self.rect.centery < 0 - 300 or self.rect.centery > 900 + 300:
            self.remove(self.groups())
            return True

    def update(self, *args):
        if self.__test_destroy():
            return

        self.__update_shoot()

    #shoot
    def shoot(self):
        self.is_shoot = True
        if self.target:
            #
            target_x, target_y = self.target.centerx, self.target.centery
            speed = math.hypot(self.vector[0], self.vector[1])
            delta_x = target_x - self.rect.centerx
            if delta_x == 0:
                speed_x = 0
                speed_y = speed
            else:
                delta_y = target_y - self.rect.centery
                ratio = delta_y / delta_x
                speed_x = math.sqrt(speed*speed / ((ratio*ratio) + 1))
                speed_y = abs(speed_x * ratio)

            if self.rect.centerx > target_x:
                speed_x *= -1
            if self.rect.centery > target_y:
                speed_y *= -1
            self.vector = [speed_x, speed_y]

    def __update_shoot(self):
        if not self.is_shoot:
            return

        self.position[0] += self.vector[0]
        self.position[1] += self.vector[1]
        self.rect.centerx = int(self.position[0])
        self.rect.centery = int(self.position[1])


#player
class Player(AbstractView):
    INITIAL_POSITION = [300, 800]

    def __init__(self, event_manager, parent_view, image=None, width=102, height=126, color=(255, 255, 255)):
        AbstractView.__init__(self, event_manager, parent_view, width, height, color)
        self.color = color
        self.speed_x = 0
        self.speed_y = 0
        self.is_shoot = False
        self.shoot_rate = 10
        self.shoot_count = 0
        self.speed_x_max = 7
        self.speed_y_max = 7
        self.is_dead = False
        self.dead_image_rate = 4
        self.dead_image_count = 0
        self._layer = 3
        self.shield = 100
        if image:
            self.image = image
        else:
            self.image = ComponentFactory.load_image('image', 'PNG', 'playerShip3_blue.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = Player.INITIAL_POSITION[0]
        self.rect.centery = Player.INITIAL_POSITION[1]
        self.__init_image()

    def __init_image(self):
        self.images = []
        self.images.append(self.image)
        self.image_index = 0
        self.image = self.images[self.image_index]

    #handle keyboard event if player press these keys plane can be moved
    def __handle_keyboard_event(self, ev):
        # event = ev.ev
        # listen key input
        key_pressed = pygame.key.get_pressed()
        # if player dead nothing would happened
        self.speed_y = 0
        self.speed_x = 0
        self.is_shoot = False

        if key_pressed[K_z] or key_pressed[K_j]:
            self.is_shoot = True

        if key_pressed[K_w] or key_pressed[K_UP]:
            self.speed_y = -self.speed_y_max
        elif key_pressed[K_s] or key_pressed[K_DOWN]:
            self.speed_y = self.speed_y_max

        if key_pressed[K_a] or key_pressed[K_LEFT]:
            self.speed_x = -self.speed_x_max
        elif key_pressed[K_d] or key_pressed[K_RIGHT]:
            self.speed_x = self.speed_x_max

    #update image
    def __update_image(self):
        if self.is_dead:
            if self.dead_image_count % self.dead_image_rate == 0:
                self.image_index = min(self.image_index + 1, len(self.images) - 1)
                if self.image_index == len(self.images) - 1:
                    self.remove(self.groups())
            self.dead_image_count += 1
        else:
            self.image_index = 0

        self.image = self.images[self.image_index]

    #update locations
    def __update_location(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > GameInstance.SCREEN_SIZE[0]:
            self.rect.right = GameInstance.SCREEN_SIZE[0]
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > GameInstance.SCREEN_SIZE[1]:
            self.rect.bottom = GameInstance.SCREEN_SIZE[1]

    #update shoot
    def __update_shoot(self):
        if self.is_shoot:
            if self.shoot_count % self.shoot_rate == 0:
                self.shoot()
            self.shoot_count += 1
        else:
            self.shoot_count = 0

    #listen for events
    def notify(self, ev):
        if isinstance(ev, KeyboardEvent):
            self.__handle_keyboard_event(ev)

    #shield for player
    def __update_shield(self):
        self.shield -= 1

    def update(self, *args):
        self.__update_shield()
        self.__update_location()
        self.__update_image()
        self.__update_shoot()

    # public method
    def shoot(self):
        bullet = Bullet(self.event_manager, self.parent_view, [0, -10], self)
        bullet.set_position(self.rect.centerx, self.rect.top)
        self.parent_view.add_view(bullet)
        bullet.shoot()
        Sound.play_bullet()

    # public method
    def destroy(self):
        Sound.play_ship_down()
        self.is_dead = True
        #todo

    def hit(self):
        if self.shield <= 0:
            self.destroy()


#enemy
class Enemy(AbstractView):
    INITIAL_POSITION = [-200, -100]

    def __init__(self, event_manager, parent_view, image=None, position=None, width=93, height=84,
                 color=(255, 255, 255)):
        AbstractView.__init__(self, event_manager, parent_view, width, height, color)
        self.color = color
        self.is_dead = False
        self.dead_image_rate = 3
        self.dead_image_count = 0
        self.route = None
        self.move_count = 0
        self._layer = 4
        self.score = 1000
        self.bullet_speed = 1
        self.hp = 1
        if image:
            self.image = image
        else:
            self.image = ComponentFactory.load_image('image', 'PNG', 'Enemies', 'enemyBlue1.png')
        self.rect = self.image.get_rect()
        if position:
            self.rect.centerx = position[0]
            self.rect.centery = position[1]
        else:
            self.rect.centerx = Enemy.INITIAL_POSITION[0]
            self.rect.centery = Enemy.INITIAL_POSITION[1]
        self.__init_image()

    #set image of enemy
    def __init_image(self):
        self.images = []
        self.images.append(self.image)
        self.image_index = 0
        self.image = self.images[self.image_index]

    #update enemy image such as enemy daed
    def __update_image(self):
        if self.is_dead:
            if self.dead_image_count % self.dead_image_rate == 0:
                self.image_index = min(self.image_index + 1, len(self.images) - 1)
                if self.image_index == len(self.images) - 1:
                    self.remove(self.groups())
            self.dead_image_count += 1
        else:
            self.image_index = 0

        self.image = self.images[self.image_index]

    def __update_location(self):
        #todo
        # to delete the auto move
        if not self.route:
            return
        self.move_count += 1
        pos = self.route.get_next()
        if pos:
            self.rect.centerx, self.rect.centery = pos[0], pos[1]
            if pos[2]:
                self.shoot()
        else:
            self.destroy()

    #listen for events
    def notify(self, ev):
        pass
        # for test
        if isinstance(ev, KeyboardEvent):
            key_pressed = pygame.key.get_pressed()
            if key_pressed[K_1]:
                self.shoot()

    def update(self, *args):
        self.__update_location()
        self.__update_image()
        self.__update_shoot()

    def __update_shoot(self):
        pass

    # public method
    def shoot(self, name="normal"):
        bullet = Bullet(self.event_manager, self.parent_view, [0, 7*self.bullet_speed], self)
        bullet.set_position(self.rect.centerx, self.rect.centery)
        bullet.target = self.parent_view.player.rect
        self.parent_view.add_view(bullet)
        bullet.shoot()

    # public method
    def destroy(self):
        self.is_dead = True

    # set the route
    def set_route(self, route):
        self.route = route

    #
    def hit(self):
        self.hp -= 1
        self.notify_all(PlayerScoreChangedEvent(random.randrange(self.score / 10, self.score / 5)))
        if self.hp <= 0:
            self.destroy()
            Sound.play_ship_down()
            self.notify_all(PlayerScoreChangedEvent(self.score))

#a class for loading creating ship
class ComponentFactory(object):
    ENEMY_BLACK_1 = "enemyBlack1"
    ENEMY_BLACK_2 = "enemyBlack2"
    ENEMY_BLACK_3 = "enemyBlack3"
    ENEMY_BLACK_4 = "enemyBlack4"
    ENEMY_BLACK_5 = "enemyBlack5"

    ENEMY_BLUE_1 = "enemyBlue1"
    ENEMY_BLUE_2 = "enemyBlue2"
    ENEMY_BLUE_3 = "enemyBlue3"
    ENEMY_BLUE_4 = "enemyBlue4"
    ENEMY_BLUE_5 = "enemyBlue5"

    ENEMY_GREEN_1 = "enemyGreen1"
    ENEMY_GREEN_2 = "enemyGreen2"
    ENEMY_GREEN_3 = "enemyGreen3"
    ENEMY_GREEN_4 = "enemyGreen4"
    ENEMY_GREEN_5 = "enemyGreen5"

    ENEMY_RED_1 = "enemyRed1"
    ENEMY_RED_2 = "enemyRed2"
    ENEMY_RED_3 = "enemyRed3"
    ENEMY_RED_4 = "enemyRed4"
    ENEMY_RED_5 = "enemyRed5"

    PLAYER_BLUE_1 = "playerShip1_blue"
    PLAYER_BLUE_2 = "playerShip2_blue"
    PLAYER_BLUE_3 = "playerShip3_blue"

    PLAYER_GREEN_1 = "playerShip1_green"
    PLAYER_GREEN_2 = "playerShip2_green"
    PLAYER_GREEN_3 = "playerShip3_green"

    PLAYER_RED_1 = "playerShip1_red"
    PLAYER_RED_2 = "playerShip2_red"
    PLAYER_RED_3 = "playerShip3_red"

    PLAYER_ORANGE_1 = "playerShip1_orange"
    PLAYER_ORANGE_2 = "playerShip2_orange"
    PLAYER_ORANGE_3 = "playerShip3_orange"

    ENEMY_SIZE = [(93, 84), (104, 84), (103, 84), (82, 84), (97, 84)]

    ENEMY_SHIPS = [ENEMY_BLACK_1, ENEMY_BLACK_2, ENEMY_BLACK_3,
                   ENEMY_BLACK_4, ENEMY_BLACK_5, ENEMY_BLUE_1,
                   ENEMY_BLUE_2, ENEMY_BLUE_3, ENEMY_BLUE_4,
                   ENEMY_BLUE_5, ENEMY_GREEN_1, ENEMY_GREEN_2,
                   ENEMY_GREEN_3, ENEMY_GREEN_4, ENEMY_GREEN_5,
                   ENEMY_RED_1, ENEMY_RED_2, ENEMY_RED_3,
                   ENEMY_RED_4, ENEMY_RED_5]

    PLAYER_SHIPS = [PLAYER_BLUE_1, PLAYER_BLUE_2, PLAYER_BLUE_3,
                    PLAYER_GREEN_1, PLAYER_GREEN_2, PLAYER_GREEN_3,
                    PLAYER_RED_1, PLAYER_RED_2, PLAYER_RED_3,
                    PLAYER_ORANGE_1, PLAYER_ORANGE_2, PLAYER_ORANGE_3]

    #a place to store image which has been loaded
    LOADED_IMAGES = {}


    @staticmethod
    def create_enemy_ship(manager, view, name):
        """
        create enemy ship

        :param manager: event manager
        :param view: main view
        :param name: the name of the ship
        """
        filename = name + ".png"
        image = ComponentFactory.load_image('image', 'PNG', 'Enemies', filename)
        size = ComponentFactory.get_ship_size(name)
        ship = Enemy(manager, view, image, width=size[0], height=size[1])
        index = random.randrange(3)
        for i in range(3):
            filename = "playerShip{}_damage{}.png".format(index + 1, i + 1)
            image = ComponentFactory.load_image('image', 'PNG', 'Damage', filename)
            ship.images.append(image)
        return ship

    @staticmethod
    def create_player_ship(manager, view, name):
        """
        create player ship

        :param manager: event manager
        :param view: main view
        :param name: the name of the ship
        """
        if not name:
            name = ComponentFactory.PLAYER_BLUE_1

        filename = name + ".png"
        image = ComponentFactory.load_image('image', 'PNG', filename)
        image = pygame.transform.smoothscale(image, [63, 50])
        ship = Player(manager, view, image, width=63, height=50)

        index = name[10]
        for i in range(3):
            filename = "playerShip{}_damage{}.png".format(index, i + 1)
            image = ComponentFactory.load_image('image', 'PNG', 'Damage', filename)
            ship.images.append(image)

        return ship

    #get the ship size to create the ship
    @staticmethod
    def get_ship_size(name):
        if name[0] == "e":
            index = int(name[-1]) - 1
            return ComponentFactory.ENEMY_SIZE[index]

        return 95, 75

    @staticmethod
    def create_number_image(number):
        # is a positive integer number
        digits = []
        if number == 0:
            digits.append(0)
        else:
            while number > 0:
                digit = number % 10
                number /= 10
                digits.append(digit)
            digits.reverse()

        images = []
        for digit in digits:
            filename = "numeral" + str(digit) + ".png"
            image = ComponentFactory.load_image('image', 'PNG', 'UI', filename)
            images.append(image)

        return images

    #load all component file
    @staticmethod
    def load_image(path, *paths):
        image = None
        if paths:
            image = ComponentFactory.load_from_memory(paths[-1])
            if image:
                return image

        image = pygame.image.load(os.path.join(path, *paths))

        if paths:
            ComponentFactory.LOADED_IMAGES[paths[-1]] = image
        else:
            ComponentFactory.LOADED_IMAGES[path] = image

        return image

    #if image has been loaded, load component from memory
    @staticmethod
    def load_from_memory(filename):
        if filename in ComponentFactory.LOADED_IMAGES:
            return ComponentFactory.LOADED_IMAGES[filename]


#game sound
class Sound():
    bullet = None
    enemy_down = None
    game_over = None
    background = None
    playing_game_over = False

    #load game bullet sound and play the sound
    @staticmethod
    def play_bullet():
        if not Sound.bullet:
            Sound.bullet = pygame.mixer.Sound(os.path.join("sound", "bullet.wav"))
            Sound.bullet.set_volume(0.3)

        Sound.bullet.play()

    #load player ship down sound and play the sound
    @staticmethod
    def play_ship_down():
        if not Sound.enemy_down:
            Sound.enemy_down = pygame.mixer.Sound(os.path.join("sound", "enemy1_down.wav"))
            Sound.enemy_down.set_volume(0.5)

        Sound.enemy_down.play()

    #load game over sound and play the sound
    @staticmethod
    def play_game_over():
        if not Sound.game_over:
            Sound.game_over = pygame.mixer.Sound(os.path.join("sound", "gameover.wav"))
            Sound.game_over.set_volume(0.3)

        Sound.game_over.play()
        Sound.playing_game_over = True

    #stop game over sound when player replay the game
    @staticmethod
    def stop_game_over():
        if Sound.game_over:
            Sound.game_over.stop()

        Sound.playing_game_over = False

    #load game background sound and play the sound
    @staticmethod
    def play_background():
        if not Sound.background:
            pygame.mixer.music.load(os.path.join("sound", "game_music.wav"))
            Sound.background = 1

        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(0.20)

    #stop to play background sound
    @staticmethod
    def stop_background():
        if Sound.background:
            pygame.mixer.music.stop()

    #check game over sound is playing or not
    @staticmethod
    def is_game_over_playing():
        return Sound.playing_game_over