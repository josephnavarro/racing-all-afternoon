import pygame
from pygame.locals import *

## Player class to represent a single racer ##
##############################################
class Player(object):
    def __init__(self, num, idno, p_index, is_title=False, player_x=None, position=None, engine=0):
        ## Load the stats from the appropriately numbered file in res/char
        self.load_data(num, idno, engine, p_index)
        ## Load the appropriate sprites
        self.load_sprites(num)
        ## Set the persona type
        self.p_index = p_index

        ## If solo mode, use the random attribute fed into the constructor
        if not is_title:
            self.player_x = player_x
            self.lane = player_x
            self.position = position
        else: ## If multiplayer mode or title, use a predefined value here
            self.player_x = 0.0
            self.lane = 0.0
            self.position = 10000

        ## Player coordinates and other attributes to move through the map
        self.player_z = None
        self.player_y = 0
        self.speed = 0
        ## The last two inputs are not used
        self.inputs = [False,False,False,False,False] ## Left, Right, Faster, Slower, Debug

        self.sprite = None        ## Sprite is not loaded by default
        self.item = None          ## Start without an item
        self.item_scrolling = 0.0 ## Whether or not we're scrolling through the item list
        self.place = 0            ## Current place in the race
        self.item_hit = 0         ## Whether or not we've been hit by an item (used for achievements)
        self.item_use = 0         ## Whether or not we've used an item (used for achievements)
        self.shake = False        ## Whether or not we're shaking out of being frozen
        self.has_boosted = 0      ## The number of times we've mini-turbo'd
        self.boost = 0.0          ## Mini-turbo accumulator, builds up to determine how much speed-up is achieved
        self.boost_diff = 0.0     ## Mini-turbo effect decrementer, applies the speed-up
        self.camera_depth = None  ## Camera distance to screen

        ## Items used for achievements
        self.used_agi = 0  ## Causes opponents to spin out
        self.used_zio = 0  ## Zaps and pushes opponents offroad
        self.used_mudo = 0 ## Blacken screen + reverse steering
        self.used_garu = 0 ## Small speed boost
        self.used_hama = 0 ## Whiten screen + reverse steering
        self.used_bufu = 0 ## Freezing projectile
        self.used_phys = 0 ## Short-range attack

        ## Item effects
        self.recover = False      ## Whether we're restoring our health
        self.no_control = 0.0     ## Whether we're spinning out of control
        self.speed_up = 0.0       ## The length of time we're sped up
        self.mudo = False         ## Whether or not we're under mudo
        self.mudo_alpha = 0       ## Personal mudo alpha value
        self.mudo_cast = False    ## Whether or not we're casting mudo
        self.mudo_cast_alpha = 0  ## Personal mudo alpha value
        self.hama = False         ## WHether or not we're under hama
        self.hama_alpha = 0       ## Personal hama alpha value
        self.hama_cast = False    ## Whether or not we're casting hama
        self.hama_cast_alpha = 0  ## Personal hama alpha value
        self.frozen = 0.0         ## The length of time we're currently frozen
        self.lightning = 0.0      ## The length of time we're affected by lightning
        self.flying = False       ## Whether or not we've been launched (jolt reaction due to being hit, for example)
        self.attack = 0.0         ## The length of time we're attacking physically
        self.accumulator = 0      ## Gravity to fall from being launched
        
        ## Personal sound effects
        try:
            self.engine01 = pygame.mixer.Sound("res/sound/engine01.ogg")
            self.engine01.set_volume(0.15)

            self.engine02 = pygame.mixer.Sound("res/sound/engine02.ogg")
            self.engine02.set_volume(0.15)

            self.engine03 = pygame.mixer.Sound("res/sound/engine03.ogg")
            self.engine03.set_volume(0.15)

            ## Item sound effects
            self.thunder = pygame.mixer.Sound("res/sound/thunder.ogg")
            self.thunder.set_volume(0.7)

            self.whoosh = pygame.mixer.Sound("res/sound/whoosh.ogg")
            self.whoosh.set_volume(0.7)

            self.whoosh_long = pygame.mixer.Sound("res/sound/long_whoosh.ogg")
            self.whoosh_long.set_volume(0.7)

            self.crash = pygame.mixer.Sound("res/sound/crash.ogg")
            self.crash.set_volume(0.7)

            self.flame = pygame.mixer.Sound("res/sound/flame.ogg")
            self.flame.set_volume(0.7)

            self.damage = pygame.mixer.Sound("res/sound/damage.ogg")
            self.damage.set_volume(0.7)

            ## Unique voices for three situations: Speeding up, hit by item, or using an item
            voice_1 = pygame.mixer.Sound("res/sound/%d/voice1.ogg" %(num+1))
            voice_2 = pygame.mixer.Sound("res/sound/%d/voice4.ogg" %(num+1))
            voice_3 = pygame.mixer.Sound("res/sound/%d/voice2.ogg" %(num+1))
            voice_4 = pygame.mixer.Sound("res/sound/%d/voice5.ogg" %(num+1))
            voice_5 = pygame.mixer.Sound("res/sound/%d/voice3.ogg" %(num+1))
            voice_6 = pygame.mixer.Sound("res/sound/%d/voice6.ogg" %(num+1))

            voice_1.set_volume(0.9)
            voice_2.set_volume(0.9)
            voice_3.set_volume(0.9)
            voice_4.set_volume(0.9)
            voice_5.set_volume(0.9)
            voice_6.set_volume(0.9)

            self.voice_speed = [voice_1, voice_2]
            self.voice_hit = [voice_3, voice_4]
            self.voice_use = [voice_5, voice_6]

            self.voice_index = 0

        except:
            pass

        self.laps = 0          ## Number of laps we've cleared
        self.lap_text_draw = 0 ## Used to flash orange

    def load_sprites(self, num):
        ## Load main image sheet
        player = pygame.image.load("res/img/player_%d.png" %(num+1))

        ## Subsurfaces for left, right, and center images
        self.player_left = player.subsurface((0,0,64,64))
        self.player_right = player.subsurface((128,0,64,64))
        self.player_straight = player.subsurface((64,0,64,64))

        ## Convert the surfaces and set their transparencies
        self.player_left = self.player_left.convert()
        self.player_right = self.player_right.convert()
        self.player_straight = self.player_straight.convert()

        self.player_left.set_colorkey((0,255,255))
        self.player_right.set_colorkey((0,255,255))
        self.player_straight.set_colorkey((0,255,255))

        ## Load frozen image sheet
        frozen = pygame.image.load("res/img/player_%d_frozen.png" %(num+1))
        
        ## Subsurfaces for left, right, and center images
        self.player_left_frozen = frozen.subsurface((0,0,64,64))
        self.player_right_frozen = frozen.subsurface((128,0,64,64))
        self.player_straight_frozen = frozen.subsurface((64,0,64,64))

        ## Convert the surfaces and set their transparencies
        self.player_left_frozen = self.player_left_frozen.convert()
        self.player_right_frozen = self.player_right_frozen.convert()
        self.player_straight_frozen = self.player_straight_frozen.convert()

        self.player_left_frozen.set_colorkey((0,255,255))
        self.player_right_frozen.set_colorkey((0,255,255))
        self.player_straight_frozen.set_colorkey((0,255,255))

    def load_data(self, num, idno, engine, p_index):
        #engine = engine/2.0 ## Scale down the impact of the engine class
        ## Player attributes for identification
        self.num = num
        self.id = idno
        self.item_choice = []         ## List of items (complete)
        self.offroad_limit_mod = 0.75 ## This is a constant
        stat_mod = [0,0,0,0,0]

        ## Get the persona data file for item list and stat mods
        f = open("res/persona/p%03d.dat" %(p_index+1)).readlines()
        for line in f:
            ## Get stat modifiers
            if line.find("name = ") != -1:
                self.persona_name = line.strip("name = ").replace("\n","")
            elif line.find("max_speed = ") != -1:
                stat_mod[0] = int(line.strip("max_speed = "))
            elif line.find("accel = ") != -1:
                stat_mod[1] = int(line.strip("accel = "))
            elif line.find("offroad = ") != -1:
                stat_mod[2] = int(line.strip("offroad = "))
            elif line.find("recovery = ") != -1:
                stat_mod[3] = int(line.strip("recovery = "))
            elif line.find("threshold = ") != -1:
                stat_mod[4] = int(line.strip("threshold = "))

            ## Get percent chances of each skill showing up and scale them to a list of 50
            elif line.find("agi = ") != -1:
                for j in range( int(float(line.strip("agi = ")) * 50)):
                    self.item_choice.append(1)
            elif line.find("bufu = ") != -1:
                for j in range( int(float(line.strip("bufu = ")) * 50 )):
                    self.item_choice.append(2)
            elif line.find("garu = ") != -1:
                for j in range( int(float(line.strip("garu = ")) * 50)):
                    self.item_choice.append(3)
            elif line.find("zio = ") != -1:
                for j in range( int(float(line.strip("zio = ")) * 50)):
                    self.item_choice.append(4)
            elif line.find("hama = ") != -1:
                for j in range( int(float(line.strip("hama = ")) * 50)):
                    self.item_choice.append(5)
            elif line.find("mudo = ") != -1:
                for j in range( int(float(line.strip("mudo = ")) * 50)):
                    self.item_choice.append(6)
            elif line.find("phys = ") != -1:
                for j in range( int(float(line.strip("phys = ")) * 50)):
                    self.item_choice.append(7)

        ## Open a character data file; note that this does not check for errors and will
        ## crash the game if the data file is not found (this should never happen, though)
        f = open("res/char/%d.dat" %(num+1)).readlines()
        for line in f:
            ## Get the name string
            if line.find("name = ") != -1:
                self.name = line.strip("name = ").replace("\n","")
            ## Get the max speed and convert it into game terms
            elif line.find("max_speed = ") != -1:
                max_speed = 0.8 + 0.012 * (int(line.strip("max_speed = ")) - 1 - engine + stat_mod[0])
                self.max_speed_mod = max_speed * 1.02
                self.braking_mod = max_speed * 0.5 * 1.02
                self.decel_mod = max_speed * 0.5 * 1.02
            ## Get the acceleration and convert it into game terms
            elif line.find("accel = ") != -1:
                accel = 1.4 + 0.4 * (int(line.strip("accel = ")) - 1 - engine + stat_mod[1])
                self.accel_mod = accel * 1.02
            ## Get the offroad mod and convert it into game terms
            elif line.find("offroad = ") != -1:
                offroad_decel = self.accel_mod + 0.24 * (7 - (int(line.strip("offroad = ")) - engine + stat_mod[2]))
                self.offroad_decel_mod = offroad_decel * 1.02
            ## Get the recovery mod and convert it into game terms
            elif line.find("recovery = ") != -1:
                self.recovery = 1.2 + 0.1 * (int(line.strip("recovery = ")) - 2 - engine + stat_mod[3])
            ## Get the mini-turbo mod and convert it into game terms
            elif line.find("threshold = ") != -1:
                self.threshold = 1.5 * (7 - (int(line.strip("threshold = ")) - engine + stat_mod[4]))
            ## Get the raw health value
            elif line.find("health = ") != -1:
                self.health = int(line.strip("health = ")) - engine*100
                self.display_health = self.health
                self.max_health = float(self.health)

