#!/usr/bin/env python
#
# Joey Navarro
#
# Licensed under the MIT License

import pygame, os, random, math
from collections import namedtuple
from pygame.locals import *
from const import *
from render import *

from course import Course
from text import Text
from player import Player

## Center the display screen
os.environ["SDL_VIDEO_CENTERED"] = "1"

## Main class that wraps the entire game logic ##
#################################################
class Main:
    def __init__(self):
        ## Initialize pygame's sound and pygame itself

        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.init()
        try:
            pygame.mixer.init()
            self.is_audio_enabled = True
            self.warning = Text("", (0,0), size=24, border=True)
        except:
            self.is_audio_enabled = False
            self.warning = Text("Warning: Sound mixer isn't working!", (0,0), size=24, border=True)

        ## Set the caption and icon
        pygame.display.set_caption("P4R: Persona 4 Racing All Afternoon")
        icon = pygame.image.load("res/img/icon.png")
        pygame.display.set_icon(icon)

        ## Fullscreen data
        self.current_dim = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.full_res = (720,480)#[int(self.current_dim[1]/float(480)*720),int(self.current_dim[1])]

        ## Load in the current options, if any
        self.load_options()

        ## FPS used to be mutable but really, there's no point in changing it anymore
        self.fps = 60.
        self.step = 1/60.
        self.clock = pygame.time.Clock()

        ## Create a default or full screen, depending on the loaded options
        if self.screen_index == 0:
            self.screen = pygame.display.set_mode((720,480),NOFRAME)
        elif self.screen_index == 1:
            self.screen = pygame.display.set_mode(self.full_res, FULLSCREEN)

        self.width = 720            ## Window width
        self.height = 480           ## Window height
        self.segments = []          ## Array of road parts
        self.items = []             ## Array of items in play
        self.resolution = None
        self.segment_length = 150.0 ## Length of segment
        self.rumble_length = 1      ## Segments per strip
        self.track_length = None    ## Calculated at runtime
        self.lanes = 2              ## Number of lanes on road
        self.unlocked = (False, False, False, False, False,
                         False, False, False, False, False) ## Whether we've unlocked characters

        ## Universal graphics stuff
        self.logo = pygame.image.load("res/img/logo.png")
        self.logo = self.logo.convert_alpha()                         ## Handles transparencies and fade-in for logo
        self.logo_mask = pygame.Surface((720,480))
        self.logo_mask.fill((255,255,255))
        self.logo_mask = self.logo_mask.convert()
        self.logo_mask.set_alpha(255)
        self.logo_alpha = 255

        self.credits_01 = pygame.image.load("res/img/credits_01.png").convert()
        self.credits_02 = pygame.image.load("res/img/credits_02.png").convert()

        self.red_arrow = pygame.image.load("res/img/red_arrow.png")
        self.yellow_arrow = pygame.image.load("res/img/yellow_arrow.png")
        self.arrow_tick = 0

        self.bg_top = pygame.Surface((self.width, self.height/3+29))
        self.bg_top = self.bg_top.convert()
        self.bg_mid = pygame.Surface((self.width, self.height*3/20))
        self.bg_mid = self.bg_mid.convert()
        self.bg_bot = pygame.Surface((self.width, self.height/3))
        self.bg_bot = self.bg_bot.convert()

        self.overlay = pygame.image.load("res/img/overlay.png").convert_alpha()
        self.bar_1 = pygame.image.load("res/img/bar_1.png").convert_alpha()
        self.bar_2 = pygame.image.load("res/img/bar_2.png").convert_alpha()
        self.bar_3 = pygame.image.load("res/img/bar_3.png").convert_alpha()
        
        self.up_arrow = pygame.image.load("res/img/up_arrow.png")
        self.down_arrow = pygame.image.load("res/img/down_arrow.png")
        self.left_arrow = pygame.image.load("res/img/left_arrow.png")
        self.right_arrow = pygame.image.load("res/img/right_arrow.png")
        self.arrow_pos = 0

        self.place_1 = pygame.image.load("res/img/place_1.png")
        self.place_2 = pygame.image.load("res/img/place_2.png")
        self.place_3 = pygame.image.load("res/img/place_3.png")
        self.place_4 = pygame.image.load("res/img/place_4.png")
        self.place_5 = pygame.image.load("res/img/place_5.png")
        self.place_6 = pygame.image.load("res/img/place_6.png")

        lightning_1 = pygame.image.load("res/img/lightning_1.png").convert_alpha()
        lightning_2 = pygame.image.load("res/img/lightning_2.png").convert_alpha()
        self.lightning_img = [lightning_1, lightning_2]

        self.portraits = []
        self.silhouettes = []
        for i in range(19):
            temp = pygame.image.load("res/img/portrait_%d.png" %(i+1))
            self.portraits.append(temp)
            if i < 17:
                temp = pygame.image.load("res/img/silhouette_%d.png" %(i+1))
                self.silhouettes.append(temp)

        ## Dialogue Box
        self.text_box = pygame.image.load("res/img/text_box.png")

        ## Persona images
        self.persona_img = []
        for i in range(84):
            temp = pygame.image.load("res/img/p%03d.png" %(i+1))
            self.persona_img.append(temp)

        ## Lit-up skill images on character selection screen
        self.small_img = []
        for i in range(7):
            temp = pygame.image.load("res/img/small_%d.png" %(i+1))
            self.small_img.append(temp)

        ## Darkened skill images on character selection screen
        self.dark_img = []
        for i in range(7):
            temp = pygame.image.load("res/img/dark_%d.png" %(i+1))
            self.dark_img.append(temp)

        ## Rotating images for menus
        self.rotate_img = []
        for i in range(10):
            temp = pygame.image.load("res/img/menu_rotate_%02d.png" %(i+1))
            self.rotate_img.append(temp)

        self.rotate_angle = 0.0

        ## Skill images for in-race purposes

        item_img_0 = pygame.image.load("res/img/mystery.png")
        item_img_1 = pygame.image.load("res/img/item_1.png")
        item_img_2 = pygame.image.load("res/img/item_2.png")
        item_img_3 = pygame.image.load("res/img/item_3.png")
        item_img_4 = pygame.image.load("res/img/item_4.png")
        item_img_5 = pygame.image.load("res/img/item_5.png")
        item_img_6 = pygame.image.load("res/img/item_6.png")
        item_img_7 = pygame.image.load("res/img/item_7.png")
        item_img_8 = pygame.image.load("res/img/item_8.png")
        item_img_9 = pygame.image.load("res/img/item_9.png")
        self.item_img = [item_img_0,item_img_1,item_img_2,item_img_3,
                         item_img_4,item_img_5,item_img_6,item_img_9,
                         item_img_7,item_img_8]

        ## Lap reminder images; we don't use text because text rending is hella slow
        lap_img_1 = pygame.image.load("res/img/lap_1.png")
        lap_img_2 = pygame.image.load("res/img/lap_2.png")
        lap_img_3 = pygame.image.load("res/img/lap_3.png")
        lap_img_4 = pygame.image.load("res/img/lap_4.png")
        lap_img_5 = pygame.image.load("res/img/lap_5.png")
        lap_img_6 = pygame.image.load("res/img/lap_6.png")
        self.lap_img = [lap_img_1,lap_img_2,lap_img_3,
                        lap_img_4,lap_img_5,lap_img_6]

        ## Give the illusion of a rotating card / spinning fireball
        self.mystery_width = 64
        self.mystery_width_increase = False
        self.fire_rot = 0.0

        ## One of the rare instances we use text rendering in-race: Counting down
        self.countdown_text = Text("", (0,0), size=256, num=2)

        self.shadow = pygame.image.load("res/img/shadow.png")
        
        ## Fade in the stage names
        self.stage_mask = pygame.Surface((720,480))
        self.stage_mask.fill((0,0,0))
        self.stage_mask = self.stage_mask.convert()
        self.stage_mask.set_alpha(255)
        self.stage_alpha = 255

        ## Strings for stage names
        self.stage_names = ["Yukiko's Castle","Steamy Bathhouse","Marukyu Striptease",
                            "Secret Laboratory","Yomotsu Hirasaka","Tartarus - Thebel",
                            "Tartarus - Arqa","Tartarus - Yabbashah","Tartarus - Tziah",
                            "Tartarus - Harabah","Tartarus - Adamah",
                            "Yasogami High","Velvet Room"]
        ## Strings for irregular button names
        self.button_names = {1001:"Hat Up", 999:"Hat Down", 990:"Hat Left", 1010:"Hat Right"}
        ## Strings for engine classes
        self.engine_string = {0:"150cc", 1:"100cc", 2:"50cc"}

        ## The named tuples that define the objects that we make literally tens of thousands of
        ## Named tuples are immutable and are thus incredibly so much faster than traditional class structures
        self.Segment = namedtuple("Segment", "index p1 p2 curve color cars")
        self.Camera = namedtuple("Camera", "x y z")
        self.Screen = namedtuple("Screen", "scale x y w")
        self.World = namedtuple("World", "x y z camera screen")
        self.Wall = namedtuple("Wall", "color offset point1 point2 point3 point4")
        self.Item = namedtuple("Item", "num level speed owner xzd")
        self.Scene = namedtuple("Scene", "pos char1 char2 bgm background lines")

        ## Sound effects
        if self.is_audio_enabled:
            self.scroll_sound = pygame.mixer.Sound("res/sound/scroll.ogg")             ## Used for item scrolling
            self.scroll_sound.set_volume(0.2)
            self.countdown_start = pygame.mixer.Sound("res/sound/countdown_start.ogg") ## Used when counting down 3, 2, 1...
            self.countdown_start.set_volume(0.2)
            self.countdown_end = pygame.mixer.Sound("res/sound/countdown_end.ogg")     ## Used to kick off a race
            self.countdown_end.set_volume(0.2)
            self.menu_sound = pygame.mixer.Sound("res/sound/menu.ogg")                 ## Used when a menu selection is made
            self.menu_sound.set_volume(0.5)
            self.select_sound = pygame.mixer.Sound("res/sound/select.ogg")             ## Used when moving through a menu
            self.select_sound.set_volume(0.5)
            self.confirm_sound = pygame.mixer.Sound("res/sound/confirm.ogg")            ## Used when moving through a menu
            self.confirm_sound.set_volume(0.5)
            self.text_scroll = pygame.mixer.Sound("res/sound/text_scroll.ogg")
            self.text_scroll.set_volume(0.9)
            
        ## Base speeds for cars
        self.max_speed = self.segment_length / self.step ## Top speed
        self.accel = self.max_speed / 5      ## Acceleration rate
        self.braking = -1 * self.max_speed   ## Deceleration for brakes
        self.decel = -1 * self.max_speed / 5 ## Natural deceleration
        self.offroad_decel = -1 * self.max_speed / 2 ## Offroad deceleration
        self.offroad_limit = self.max_speed / 2      ## Speed limit when offroad

        ## Other global images
        self.subscreen1 = pygame.Surface((self.width, self.height))       ## The main screen to draw to; can be scaled
        self.pause_subscreen = pygame.Surface((self.width, self.height))  ## The pause screen that displays when pause is on
        self.pause_subscreen = self.pause_subscreen.convert()
        self.pause_subscreen.fill((255,255,255))

        self.icon_subscreen = pygame.Surface((60,60))
        self.icon_subscreen = self.icon_subscreen.convert()
        self.icon_subscreen.fill((255,255,255))
        self.icon_subscreen.set_alpha(0)
        self.icon_alpha = 0

        ## Transparency masks for displaying darkening and whitening due to hama or mudo
        self.hama_mask = pygame.Surface((self.width, self.height))
        self.hama_mask.fill((255,255,255))
        self.hama_mask = self.hama_mask.convert()

        self.mudo_mask = pygame.Surface((self.width, self.height))
        self.mudo_mask.fill((0,0,0))
        self.mudo_mask = self.mudo_mask.convert()

        ## Load the title splash
        self.title_img = pygame.image.load("res/img/title_img.png")
        self.title_back = []
        for i in range(1,8):
            temp = pygame.image.load("res/img/title_back_%02d.png" %i)
            self.title_back.append(temp)

        self.menu_back = []
        for i in range(1,6):
            temp = pygame.image.load("res/img/menu_back_%02d.png" %i)
            self.menu_back.append(temp)

        ## Joystick initialization
        pygame.joystick.init()
        self.js_list = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.js_list:
            j.init()

    def load_options(self):
        ## Load options from data file
        try:
            f = open("res/data/options.dat", "r").readlines()
            for line in f:
                ## Whether screen is windowed or full
                if line.find("screen_index = ") != -1:
                    self.screen_index = int(line.strip("screen_index = "))
                ## How far to make the draw distance
                elif line.find("interface_index = ") != -1:
                    self.interface_index = int(line.strip("interface_index = "))
                ## Whether or not BGM is playing
                elif line.find("music_index = ") != -1:
                    if self.is_audio_enabled:
                        self.music_index = int(line.strip("music_index = "))
                    else:
                        self.music_index = 1
                ## Whether we should play sound effects
                elif line.find("sound_index = ") != -1:
                    if self.is_audio_enabled:
                        self.sound_index = int(line.strip("sound_index = "))
                    else:
                        self.sound_index = 1
                ## What kind of input we should restrict ourselves to
                elif line.find("input_index = ") != -1:
                    self.input_index = int(line.strip("input_index = "))
                ## Gamepad button mapping
                elif line.find("gamepad = ") != -1:
                    gamepad = line.strip("gamepad = ").split(",")
                    for i in range(len(gamepad)):
                        gamepad[i] = int(gamepad[i])
                    self.gamepad = gamepad
                ## Engine class (50cc, 100cc, 150cc)
                elif line.find("engine_class = ") != -1:
                    self.engine_class = int(line.strip("engine_class = "))
        except (IOError, IndexError, ValueError):
            try:
                os.makedirs("res/data")
            except OSError:
                pass

            f = open("res/data/options.dat", "w")

            ## Windowed
            self.screen_index = 0
            f.write("screen_index = 0\n")
            ## Near draw distance
            self.interface_index = 0
            f.write("interface_index = 0\n")
            if self.is_audio_enabled:
                ## Music playing
                self.music_index = 0
                f.write("music_index = 0\n")
                ## Sounds playing
                self.sound_index = 0
                f.write("sound_index = 0\n")
            else:
                ## Music not playing
                self.music_index = 1
                f.write("music_index = 1\n")
                ## Sounds not playing
                self.sound_index = 1
                f.write("sound_index = 1\n")
            ## No input restriction
            self.input_index = 0
            f.write("input_index = 0\n")
            ## No buttons set
            self.gamepad = [-1] * 7
            f.write("gamepad = -1,-1,-1,-1,-1,-1,-1\n")
            ## 100cc
            self.engine_class = 1
            f.write("engine_class = 1\n")

            f.close()

    def write_options(self):
        ## Save current session's option settings and control config
        try:
            f = open("res/data/options.dat", "r+")
            f.seek(0)
            f.flush()
            ## Write current options to file
            f.write("screen_index = %d\n" %self.screen_index)
            f.write("interface_index = %d\n" %self.interface_index)
            f.write("music_index = %d\n" %self.music_index)
            f.write("sound_index = %d\n" %self.sound_index)
            f.write("input_index = %d\n" %self.input_index)
            f.write("gamepad = ")
            for i in range(7):
                f.write("%d" %self.gamepad[i])
                if i != 6:
                    f.write(",")
            f.write("\n")
            f.write("engine_class = %d\n" %self.engine_class)

            f.close()
        except (IOError, IndexError, ValueError):
            try:
                os.makedirs("res/data")
            except OSError:
                pass
            ## Make a new file and write current options to it
            f = open("res/data/options.dat", "w")
            f.write("screen_index = %d\n" %self.screen_index)
            f.write("interface_index = %d\n" %self.interface_index)
            f.write("music_index = %d\n" %self.music_index)
            f.write("sound_index = %d\n" %self.sound_index)
            f.write("input_index = %d\n" %self.input_index)
            f.write("gamepad = ")
            for i in range(7):
                f.write("%d" %self.gamepad[i])
                if i != 6:
                    f.write(",")
            f.write("\n")
            f.write("engine_class = %d\n" %self.engine_class)

            f.close()

    def splash(self):
        ## The splash screen that plays when you boot up the game
        not_yet = True ## Not yet time to display the main menu
        self.logo_alpha = 255 ## Alpha transparency for main logo is 100% opaque

        ## If we're exiting a race prematurely, stop the countdown noises
        if self.sound_index == 0:
            self.countdown_start.stop()
            self.countdown_end.stop()
        if self.music_index == 0:
            pygame.mixer.music.stop()

        while not_yet: ## While we're not displaying the main menu
            self.clock.tick(self.fps)
            self.subscreen1.fill((255,255,255))
            self.subscreen1.blit(self.logo, self.logo.get_rect(center=(180*2,120*2)))
            self.warning.update(pos=(0,480-48), right=700)
            self.warning.draw(self.subscreen1)
            self.subscreen1.blit(self.logo_mask, (0,0))

            ## Fade out logo
            if self.logo_alpha > 255:
                self.logo_mask.set_alpha(min(255,int(275-self.logo_alpha)))
            ## Fade in logo
            else:
                self.logo_mask.set_alpha(max(0,int(self.logo_alpha)))
            if self.logo_alpha <= -100:
                not_yet = False ## If it's fully faded in, start the game proper

            ## Full screen mode
            if self.screen_index == 1:
                pygame.transform.smoothscale(self.subscreen1,self.full_res, self.screen)
            ## Windowed mode
            else:
                self.screen.blit(self.subscreen1, (0,0))

            pygame.display.flip()

            ## Fade the screen
            self.logo_alpha -= 3 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

            ## Allow player to exit out of the game window
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self._quit()

        ## Load the title screen BGM
        if self.music_index == 0:
            pygame.mixer.music.load("res/sound/bgm01.ogg")
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)
        ## Enter title screen
        self.title()
        ## Close everything once title screen is done
        return

    def update_car(self, car, old_segment, new_segment):
        ## Update the car's segmented position
        if old_segment != new_segment:
            old_segment.cars.remove(car)
            new_segment.cars.append(car)

    def reset(self, players, is_title, course):
        ## Reset the entire rendering module
        self.has_changed_music = False ## We have not changed music to end-of-race
        self.gravity = -3              ## Gravitational constant
        self.pause = False             ## We are not pausing
        self.pause_index = 0           ## Pause menu choice is at the top
        self.has_written = False       ## We have not written achievements to file
        self.road_width = 1600     ## -1600 to 1600
        self.field_of_view = 156   ## Angle in degrees
        self.camera_height = 800   ## Z-height of camera
        self.width = 720           ## Render size
        self.height = 480          ## Render size
        self.lanes = int(self.lanes)   ## Number of lanes to draw
        self.road_width = int(self.road_width)          ## Width of road
        self.camera_height = int(self.camera_height)    ## Camera height from ground
        self.field_of_view = int(self.field_of_view)    ## Field of view angle
        self.segment_length = int(self.segment_length)  ## Length of a segment
        self.rumble_length = int(self.rumble_length)    ## Length of a rumble strip

        self.draw_distance = 50  ## Number of segments to draw
        self.draw_distance = int(self.draw_distance)

        ## Set camera depth and z camera value for all players
        for player in players:
            player.camera_depth = 1 / math.tan((self.field_of_view/2) * 3.14159 / 180.0)
            player.player_z = self.camera_height * player.camera_depth

        self.resolution = self.height / 300
        self.reset_road(is_title, course)  ## Reset the road objects

        self.max_laps = 4  ## Maximum laps is 3, but we add 1 at the beginning of the race
        self.subscreens = [self.subscreen1]  ## Single player uses the same subscreen

        self.time = 0.0 ## Time is used only for achievement purposes
        self.get_new_lap(True) ## Get a new lap at the very start
        self.cpu_mudo = 0   ## Number of times the CPU's have used Mudo
        self.cpu_hama = 0   ## Number of times the CPU's have used Hama
        self.cpu_zio = 0    ## Number of times the CPU's have used Zio
        self.fade_alpha = 0 ## Fade mask for Mudo and Hama?

    def get_cpu_inputs(self, dt):
        ## Players 2 through 6
        for i in range(1,len(self.players)):
            self.players[i].shake = False      ## Not shaking
            self.players[i].inputs[0] = False  ## Not steering
            self.players[i].inputs[1] = False  ## Not steering
            self.players[i].inputs[2] = False  ## Not accelerating

            ## Do things if not spinning out and not frozen
            if self.players[i].no_control <= 0 and self.players[i].frozen <= 0:
                ## Find the current segment we're on for reference
                segment = self.find_segment(self.players[i].position)

                ## Steer left
                if (segment.curve < 0 and self.players[i].player_x > self.players[i].lane) or\
                   self.players[i].player_x > 1:
                    if self.players[i].hama_alpha <= 0 and self.players[i].mudo_alpha <= 0:
                        self.players[i].inputs[0] = True
                        if self.players[i].lightning <= 0:
                            self.players[i].boost += 0.04 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    else:
                        ## Reverse steering if under hama or mudo
                        self.players[i].inputs[1] = True

                ## Steer right
                elif (segment.curve > 0 and self.players[i].player_x < self.players[i].lane) or\
                     self.players[i].player_x < -1:
                    if self.players[i].hama_alpha <= 0 and self.players[i].mudo_alpha <= 0:
                        self.players[i].inputs[1] = True
                        if self.players[i].lightning <= 0:
                            self.players[i].boost += 0.04 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    else:
                        ## Reverse steering if under hama or mudo
                        self.players[i].inputs[0] = True
                else:
                    ## If we're not steering, decrease the mini-turbo
                    if self.players[i].boost > self.players[i].boost_diff:
                        self.players[i].boost_diff = self.players[i].boost
                    self.players[i].boost -= 0.1 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    if self.players[i].boost < 0:
                        self.players[i].boost += 0.1 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

                self.players[i].inputs[2] = True ## Accelerate

                ## If we have a skill, 2% chance to use it every frame
                if self.players[i].item != None and random.randint(1,50) == 1 and self.players[i].item_scrolling <= 0.0:
                    ## Small chance to play "item use" voice once
                    talk = random.randint(1,3)
                    if talk == 1 and self.sound_index == 0:
                        if self.players[i].voice_use[self.players[i].voice_index].get_num_channels() == 0:
                            self.players[i].voice_use[self.players[i].voice_index].play()
                            self.players[i].voice_index = 1 if self.players[i].voice_index == 0 else 0
                    ## Skill 1 - Agi - Launches three fireball projectiles that follow the road
                    if self.players[i].item == 1:
                        ## Play whoosh sound to signify launch
                        if self.sound_index == 0:
                            self.stop_all_sounds()
                            self.players[i].whoosh.play()
                        self.add_item(8, self.players[i].position+self.segment_length*2,
                                      self.players[i].player_x,
                                      max(self.players[i].speed, self.max_speed*2),
                                      i, 3)
                        ## Remove item from player
                        self.players[i].item = None
                    ## Skill 2 - Bufu - Launches one ice chunk that follows the road and freezes on contact
                    elif self.players[i].item == 2:
                        ## Play whoosh sound to signify launch
                        if self.sound_index == 0:
                            self.stop_all_sounds()
                            self.players[i].whoosh.play()
                        ## Add the ice projectile
                        self.add_item(9, self.players[i].position + self.segment_length*2,
                                      self.players[i].player_x,
                                      max(self.players[i].speed, self.max_speed*2),
                                      i, 3)
                        ## Remove item from player
                        self.players[i].item = None
                    ## Skill 3 - Garu - Grants a temporary speed boost
                    elif self.players[i].item == 3:
                        ## Play long whoosh to signify speedup
                        if self.sound_index == 0:
                            self.stop_all_sounds()
                            self.players[i].whoosh_long.play()
                            ## Small chance to play "zooming" voice clip
                            if talk > 1 and self.sound_index == 0:
                                if self.players[i].voice_speed[self.players[i].voice_index].get_num_channels() == 0:
                                    self.players[i].voice_speed[self.players[i].voice_index].play()
                                    self.players[i].voice_index = 1 if self.players[i].voice_index == 0 else 0
                        self.players[i].speed_up = 0.3 * 2
                        self.players[i].speed = self.max_speed * 1.5
                        ## Remove item from player
                        self.players[i].item = None
                    ## Skill 4 - Zio - Zaps all players ahead of you and pushes them offroad
                    elif self.players[i].item == 4:
                        for p in range(len(self.players)):
                            if p != i and self.players[p].place < self.players[i].place and self.players[p].laps != self.max_laps and not self.players[p].recover:
                                if self.sound_index == 0:
                                    self.stop_all_sounds()
                                    self.players[p].thunder.play()
                                ## Negative/positive signifies left or right pushing
                                self.players[p].lightning += random.choice((-1,1)) * (0.5 + self.players[p].place / 16.0)

                                self.players[p].flying = True ## Player gets launched a little when hit
                                self.players[p].boost = -1    ## Cannot turbo out of it
                                self.players[p].no_control += abs(self.players[p].lightning) ## A little out of control
                                self.players[p].item_hit += 1
                                self.players[p].health -= 25
                        ## Remove item from player
                        self.players[i].item = None
                    ## Skill 5 - Hama - Reverses the steering of all players ahead of you
                    elif self.players[i].item == 5:
                        for p in range(len(self.players)):
                            ## Don't affect people who are under hama/mudo or who are using hama/mudo
                            if p != i and self.players[p].hama_alpha <= 0 and self.players[p].mudo_alpha <= 0 and\
                               self.players[p].hama_cast_alpha <= 0 and self.players[p].mudo_cast_alpha <= 0 and\
                               self.players[p].no_control <= 0 and self.players[p].frozen <= 0 and\
                               self.players[p].place < self.players[i].place:
                                self.players[p].hama = True
                                self.players[p].item_hit += 1
                        ## Remove player item
                        self.players[i].item = None
                    ## Skill 6 - Mudo - Reverses the steering of all players ahead of you
                    elif self.players[i].item == 6:
                        for p in range(len(self.players)):
                            ## Don't affect people who are under hama/mudo or who are using hama/mudo
                            if p != i and self.players[p].hama_alpha <= 0 and self.players[p].mudo_alpha <= 0 and\
                               self.players[p].hama_cast_alpha <= 0 and self.players[p].mudo_cast_alpha <= 0 and\
                               self.players[p].no_control <= 0 and self.players[p].frozen <= 0 and\
                               self.players[p].place < self.players[i].place:
                                self.players[p].mudo = True
                                self.players[p].item_hit += 1
                        ## Remove player item
                        self.players[i].item = None
                    ## Skill 7 - Physical - Damages opponents in a small radius
                    elif self.players[i].item == 7:
                        self.players[i].attack = 90 ## Set the attack radius
                        ## Remove player item
                        self.players[i].item = None

    def get_inputs(self, dt, is_done):
        ## Get human player inputs
        if not self.pause: ## If we're not paused...
            self.players[0].shake = False     ## Not shaking
            self.players[0].inputs[2] = False ## Not accelerating
            self.players[0].inputs[1] = False ## Not steering
            self.players[0].inputs[0] = False ## Not steering

            if self.input_index != 2:
                ## If we aren't restricted to the controller, get keyboard
                key = pygame.key.get_pressed()        ## Poll for keys pressed, to allow for pre-countdown acceleration
                if key[pygame.K_UP]:                  ## UP ARROW accelerates
                    self.players[0].inputs[2] = True

                if key[pygame.K_LEFT]:  ## LEFT ARROW steers left
                    if self.players[0].no_control <= 0 and self.players[0].frozen <= 0:
                        if self.players[0].hama_alpha <= 0 and self.players[0].mudo_alpha <= 0:
                            self.players[0].inputs[0] = True
                            if self.players[0].lightning <= 0:
                                self.players[0].boost += 0.04 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                        else:
                            ## Reverse steering if under hama/mudo
                            self.players[0].inputs[1] = True

                elif key[pygame.K_RIGHT]: ## RIGHT ARROW steers right
                    if self.players[0].no_control <= 0 and self.players[0].frozen <= 0:
                        if self.players[0].hama_alpha <= 0 and self.players[0].mudo_alpha <= 0:
                            self.players[0].inputs[1] = True
                            if self.players[0].lightning <= 0:
                                self.players[0].boost += 0.04 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                        else:
                            ## Reverse steering if under hama/mudo
                            self.players[0].inputs[0] = True

            if len(self.js_list) >= 1 and self.input_index != 1:
                ## If we aren't restricted to the keyboard and we have at least one controller, get controller
                for j in range(len(self.js_list)):
                    try:
                        if self.js_list[j].get_button(self.gamepad[4]): ## Poll for accelerate button
                            self.players[0].inputs[2] = True
                    except:
                        pass

                    ## Grab joystick hats, but note that this only will work on Windows
                    try:
                        ## Wrapped in a try-except so that if we can't load a hat or the hat is invalid
                        ## for some reason, we don't crash
                        if self.js_list[j].get_numhats() != 0:
                            e = self.js_list[j].get_hat(0)
                            ## Gamepad hats are recognized by this program as a single integer, but the
                            ## actual return value is a tuple. Thus to convert into a single integer,
                            ## we do arithmetic shenanigans and offset by 1000 so it doesn't collide with
                            ## actual button mappings
                            if e[0]*10 + e[1] + 1000 == self.gamepad[2]:
                                if self.players[0].no_control <= 0 and self.players[0].frozen <= 0:
                                    if self.players[0].hama_alpha <= 0 and self.players[0].mudo_alpha <= 0:
                                        self.players[0].inputs[0] = True
                                        if self.players[0].lightning <= 0:
                                            self.players[0].boost += 0.04 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                                    else:
                                        ## Reverse steering if under hama/mudo
                                        self.players[0].inputs[1] = True
                            ## Same arithmetic shenanigans
                            elif e[0]*10 + e[1] + 1000 == self.gamepad[3]:
                                if self.players[0].no_control <= 0 and self.players[0].frozen <= 0:
                                    if self.players[0].hama_alpha <= 0 and self.players[0].mudo_alpha <= 0:
                                        self.players[0].inputs[1] = True
                                        if self.players[0].lightning <= 0:
                                            self.players[0].boost += 0.04 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                                    else:
                                        ## Reverse steering if under hama/mudo
                                        self.players[0].inputs[0] = True
                    except:
                        pass

                    ## Grab buttons for steering. Windows uses hats but can be configured to use buttons.
                    try:
                        ## Wrapped in a try-except because I'm paranoid that the button polling will act up
                        ## on someone's computer if they have a weird keyboard setup
                        if self.js_list[j].get_button(self.gamepad[2]):
                            if self.players[0].no_control <= 0 and self.players[0].frozen <= 0:
                                if self.players[0].hama_alpha <= 0 and self.players[0].mudo_alpha <= 0:
                                    self.players[0].inputs[0] = True
                                    if self.players[0].lightning <= 0:
                                        self.players[0].boost += 0.04 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                                else:
                                    ## Reverse steering if under hama/mudo
                                    self.players[0].inputs[1] = True

                        elif self.js_list[j].get_button(self.gamepad[3]):
                            if self.players[0].no_control <= 0 and self.players[0].frozen <= 0:
                                if self.players[0].hama_alpha <= 0 and self.players[0].mudo_alpha <= 0:
                                    self.players[0].inputs[1] = True
                                    if self.players[0].lightning <= 0:
                                        self.players[0].boost += 0.04 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                                else:
                                    ## Reverse steering if under hama/mudo
                                    self.players[0].inputs[0] = True
                    except:
                        pass

        ## If we're not steering, decrease the turbo accumulator and/or launch into a mini-turbo
        if not self.players[0].inputs[0] and not self.players[0].inputs[1]:
            if self.players[0].boost > self.players[0].boost_diff:
                self.players[0].boost_diff = self.players[0].boost
            self.players[0].boost -= 0.1 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
            if self.players[0].boost < 0:
                self.players[0].boost += 0.1 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

        ## Poll the event queue for inputs
        for e in pygame.event.get():
            ## Allow players to exit out manually at any time
            if e.type == pygame.QUIT:
                self._quit() ## Safe quit method

            ## One-off joystick hat motion detection; we do not use this for steering because
            ## this only grabs a single hat event, not a continuous one
            elif e.type == pygame.JOYHATMOTION:
                ## If we're paused, manipulate pause menu
                if self.pause:
                    if self.sound_index == 0 and e.value != (0,0):
                        self.select_sound.play()
                    if e.value[0]*10 + e.value[1] + 1000 == self.gamepad[0]:
                        self.pause_index -= 1
                        if self.pause_index < 0:
                            self.pause_index = 1
                    elif e.value[0]*10 + e.value[1] + 1000 == self.gamepad[1]:
                        self.pause_index += 1
                        if self.pause_index > 1:
                            self.pause_index = 0
                else: ## If in-game, shake out of frozen or stun if applicable
                    if self.players[0].no_control > 0:
                        self.players[0].no_control -= 0.1
                        self.players[0].shake = True
                    if self.players[0].frozen > 0:
                        self.players[0].frozen -= 0.1
                        self.players[0].shake = True

            ## Grab a one-off button press. We do not use this for acceleration or steering
            ## because this only understands single events, not continuous ones
            elif e.type == pygame.JOYBUTTONDOWN:
                ## If we're in the pause menu, manipulate the menu
                if self.pause:
                    if e.button == self.gamepad[4]:
                        if self.sound_index == 0:
                            self.confirm_sound.play()
                        if self.pause_index == 0:
                            ## Resume the race
                            self.pause = False
                        elif self.pause_index == 1:
                            ## Exit the race
                            for p in self.players:
                                p.engine01.stop()
                                p.engine02.stop()
                                p.engine03.stop()
                            if self.music_index == 0:
                                pygame.mixer.music.stop()
                            return True
                    elif e.button == self.gamepad[0]:
                        if self.sound_index == 0:
                            self.select_sound.play()
                        self.pause_index -= 1
                        if self.pause_index < 0:
                            self.pause_index = 1
                    elif e.button == self.gamepad[1]:
                        if self.sound_index == 0:
                            self.select_sound.play()
                        self.pause_index += 1
                        if self.pause_index > 1:
                            self.pause_index = 0
                ## If we're not restriced to the keyboard...
                elif self.input_index != 1:
                    ## Pause button
                    if e.button == self.gamepad[6]:
                        for p in range(len(self.players)):
                            if self.players[p].engine03.get_num_channels() > 0:
                                self.players[p].engine03.stop()
                            if self.players[p].engine02.get_num_channels() > 0:
                                self.players[p].engine02.stop()
                            if self.players[p].engine01.get_num_channels() > 0:
                                self.players[p].engine01.stop()
                        self.pause = True
                    else:
                        ## If not frozen or out of control...
                        if self.players[0].no_control <= 0 and self.players[0].frozen <= 0:

                            if e.button == self.gamepad[5]: ## Item use button
                                ## Note that the skill usage described here is exactly the same as the skill
                                ## usage described in the get_cpu_inputs method above. As such I will not
                                ## repeat myself here. Just scroll down to the next branch if you want.

                                if self.players[0].item != None and self.players[0].item_scrolling <= 0.0:
                                        self.players[0].item_use += 1
                                        talk = random.randint(1,3)
                                        if talk == 1 and self.sound_index == 0:
                                            if self.players[0].voice_use[self.players[0].voice_index].get_num_channels() == 0:
                                                self.players[0].voice_use[self.players[0].voice_index].play()
                                                self.players[0].voice_index = 1 if self.players[0].voice_index == 0 else 0
                                        ## Skill 1 - Agi
                                        if self.players[0].item == 1:
                                            if self.sound_index == 0:
                                                self.stop_all_sounds()
                                                self.players[0].whoosh.play()
                                            self.add_item(8, self.players[0].position+self.segment_length*2,
                                                          self.players[0].player_x,
                                                          max(self.players[0].speed, self.max_speed*2),
                                                          e.joy, 3)
                                            self.players[0].item = None
                                            self.players[0].used_agi += 1
                                        ## Skill 2 - Bufu
                                        elif self.players[0].item == 2:
                                            if self.sound_index == 0:
                                                self.stop_all_sounds()
                                                self.players[0].whoosh.play()
                                            self.add_item(9, self.players[0].position + self.segment_length*2,
                                                          self.players[0].player_x,
                                                          max(self.players[0].speed, self.max_speed*2),
                                                          e.joy, 3)
                                            self.players[0].item = None
                                            self.players[0].used_bufu += 1
                                        ## Skill 3 - Garu
                                        elif self.players[0].item == 3:
                                            if self.sound_index == 0:
                                                self.stop_all_sounds()
                                                self.players[0].whoosh_long.play()
                                                if talk > 1 and self.sound_index == 0:
                                                    if self.players[0].voice_speed[self.players[0].voice_index].get_num_channels() == 0:
                                                        self.players[0].voice_speed[self.players[0].voice_index].play()
                                                        self.players[0].voice_index = 1 if self.players[0].voice_index == 0 else 0
                                            self.players[0].speed_up = 0.3 * 2
                                            self.players[0].speed = self.max_speed * 1.5
                                            self.players[0].item = None
                                            self.players[0].used_garu += 1
                                        ## Skill 4 - Zio
                                        elif self.players[0].item == 4:
                                            for p in range(len(self.players)):
                                                if p != e.joy and self.players[p].place < self.players[0].place and self.players[p].laps != self.max_laps and not self.players[p].recover:
                                                    if self.sound_index == 0:
                                                        self.stop_all_sounds()
                                                        self.players[p].thunder.play()
                                                    self.players[p].lightning += random.choice((-1,1)) * (0.5 + self.players[p].place / 16.0)
                                                    self.players[p].flying = True
                                                    self.players[p].boost = -1
                                                    self.players[p].no_control += abs(self.players[p].lightning)
                                                    self.players[p].item_hit += 1
                                                    self.players[p].health -= 25

                                            self.players[0].item = None
                                            self.players[0].used_zio += 1
                                        ## Skill 5 - Hama
                                        elif self.players[0].item == 5:
                                            for p in range(len(self.players)):
                                                if p != e.joy and self.players[p].hama_alpha <= 0 and self.players[p].mudo_alpha <= 0 and\
                                                   self.players[p].hama_cast_alpha <= 0 and self.players[p].mudo_cast_alpha <= 0 and\
                                                   self.players[p].no_control <= 0 and self.players[p].frozen <= 0 and\
                                                   self.players[p].place < self.players[0].place:
                                                    self.players[p].hama = True
                                                    self.players[p].item_hit += 1

                                            self.players[0].item = None
                                            self.players[0].hama_cast = True
                                            self.players[0].used_hama += 1
                                        ## Skill 6 - Mudo
                                        elif self.players[0].item == 6:
                                            for p in range(len(self.players)):
                                                if p != e.joy and self.players[p].hama_alpha <= 0 and self.players[p].mudo_alpha <= 0 and\
                                                   self.players[p].hama_cast_alpha <= 0 and self.players[p].mudo_cast_alpha <= 0 and\
                                                   self.players[p].no_control <= 0 and self.players[p].frozen <= 0 and\
                                                   self.players[p].place < self.players[0].place:

                                                    self.players[p].mudo = True
                                                    self.players[p].item_hit += 1

                                            self.players[0].item = None
                                            self.players[0].mudo_cast = True
                                            self.players[0].used_mudo += 1
                                        ## Skill 7 - Physical
                                        elif self.players[0].item == 7:
                                            self.players[0].attack = 90
                                            self.players[0].item = None
                                            self.players[0].used_phys += 1

            ## Get key presses. We use polling to get driving commands because these are non-continuous,
            ## one-shot events
            elif e.type == pygame.KEYDOWN:
                ## Pause if we press ESC or if it's the end of the race, and if we're not currently paused
                if e.key == pygame.K_ESCAPE or (e.key in [pygame.K_BACKSPACE, pygame.K_SPACE, pygame.K_z, pygame.K_RETURN] and\
                                                self.players[0].laps == self.max_laps and is_done and not self.pause):
                    for p in range(len(self.players)):
                        if self.players[p].engine03.get_num_channels() > 0:
                            self.players[p].engine03.stop()
                        if self.players[p].engine02.get_num_channels() > 0:
                            self.players[p].engine02.stop()
                        if self.players[p].engine01.get_num_channels() > 0:
                            self.players[p].engine01.stop()
                    self.pause = True
                ## If we're paused, manipulate the pause menu
                elif self.pause:
                    if e.key in [pygame.K_UP, pygame.K_w]:
                        if self.sound_index == 0:
                            self.select_sound.play()
                        self.pause_index -= 1
                        if self.pause_index < 0:
                            self.pause_index = 1
                    elif e.key in [pygame.K_DOWN, pygame.K_s]:
                        if self.sound_index == 0:
                            self.select_sound.play()
                        self.pause_index += 1
                        if self.pause_index > 1:
                            self.pause_index = 0
                    elif e.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                        if self.sound_index == 0:
                            self.confirm_sound.play()
                        if self.pause_index == 0:
                            ## Return to game
                            self.pause = False
                        elif self.pause_index == 1:
                            ## Quit game
                            for p in self.players:
                                p.engine01.stop()
                                p.engine02.stop()
                                p.engine03.stop()
                            if self.is_audio_enabled:
                                pygame.mixer.music.stop()
                            return True

                ## If we're not restricted to the controller...
                elif self.input_index != 2:
                    ## If not frozen or out of control...
                    if self.players[0].no_control <= 0 and self.players[0].frozen <= 0:
                        if e.key == pygame.K_z:
                            ## Note that the skill usage described here is exactly the same as the skill
                            ## usage described in the get_cpu_inputs method above. As such I will not
                            ## repeat myself here. Just scroll down to the next branch if you want.
                            if self.players[0].item != None and self.players[0].item_scrolling <= 0.0:
                                self.players[0].item_use += 1
                                talk = random.randint(1,3)
                                if talk == 1 and self.sound_index == 0:
                                    if self.players[0].voice_use[self.players[0].voice_index].get_num_channels() == 0:
                                        self.players[0].voice_use[self.players[0].voice_index].play()
                                        self.players[0].voice_index = 1 if self.players[0].voice_index == 0 else 0
                                ## Skill 1 - Agi
                                if self.players[0].item == 1:
                                    if self.sound_index == 0:
                                        self.stop_all_sounds()
                                        self.players[0].whoosh.play()
                                    self.add_item(8, self.players[0].position+self.segment_length*2,
                                                  self.players[0].player_x,
                                                  max(self.players[0].speed, self.max_speed*2),
                                                  0,3)
                                    self.players[0].item = None
                                    self.players[0].used_agi += 1
                                ## Skill 2 - Bufu
                                elif self.players[0].item == 2:
                                    if self.sound_index == 0:
                                        self.stop_all_sounds()
                                        self.players[0].whoosh.play()
                                    self.add_item(9, self.players[0].position + self.segment_length*2,
                                                  self.players[0].player_x,
                                                  max(self.players[0].speed, self.max_speed*2),
                                                  0,3)
                                    self.players[0].item = None
                                    self.players[0].used_bufu += 1
                                ## Skill 3 - Garu
                                elif self.players[0].item == 3:
                                    if self.sound_index == 0:
                                        self.stop_all_sounds()
                                        self.players[0].whoosh_long.play()
                                        if talk > 1 and self.sound_index == 0:
                                            if self.players[0].voice_speed[self.players[0].voice_index].get_num_channels() == 0:
                                                self.players[0].voice_speed[self.players[0].voice_index].play()
                                                self.players[0].voice_index = 1 if self.players[0].voice_index == 0 else 0
                                    self.players[0].speed_up = 0.3 * 2
                                    self.players[0].speed = self.max_speed * 1.5
                                    self.players[0].item = None
                                    self.players[0].used_garu += 1
                                ## Skill 4 - Zio
                                elif self.players[0].item == 4:
                                    for p in range(len(self.players)):
                                        if p != 0 and self.players[p].place < self.players[0].place and self.players[p].laps != self.max_laps and not self.players[p].recover:
                                            if self.sound_index == 0:
                                                self.stop_all_sounds()
                                                self.players[p].thunder.play()
                                            self.players[p].lightning += random.choice((-1,1)) * (0.5 + self.players[p].place / 16.0)
                                            self.players[p].flying = True
                                            self.players[p].boost = -1
                                            self.players[p].no_control += abs(self.players[p].lightning)
                                            self.players[p].item_hit += 1
                                            self.players[p].health -= 25

                                    self.players[0].item = None
                                    self.players[0].used_zio += 1
                                ## Skill 5 - Hama
                                elif self.players[0].item == 5:
                                    for p in range(len(self.players)):
                                        if p != 0 and self.players[p].hama_alpha <= 0 and self.players[p].mudo_alpha <= 0 and\
                                           self.players[p].hama_cast_alpha <= 0 and self.players[p].mudo_cast_alpha <= 0 and\
                                           self.players[p].no_control <= 0 and self.players[p].frozen <= 0 and\
                                           self.players[p].place < self.players[0].place:
                                            self.players[p].hama = True
                                            self.players[p].item_hit += 1

                                    self.players[0].item = None
                                    self.players[0].hama_cast = True
                                    self.players[0].used_hama += 1
                                ## Skill 6 - Mudo
                                elif self.players[0].item == 6:
                                    for p in range(len(self.players)):
                                        if p != 0 and self.players[p].hama_alpha <= 0 and self.players[p].mudo_alpha <= 0 and\
                                           self.players[p].hama_cast_alpha <= 0 and self.players[p].mudo_cast_alpha <= 0 and\
                                           self.players[p].no_control <= 0 and self.players[p].frozen <= 0 and\
                                           self.players[p].place < self.players[0].place:
                                            self.players[p].mudo = True
                                            self.players[p].item_hit += 1

                                    self.players[0].item = None
                                    self.players[0].used_mudo += 1
                                    self.players[0].mudo_cast = True
                                ## Skill 7 - Physical
                                elif self.players[0].item == 7:
                                    self.players[0].attack = 90
                                    self.players[0].item = None
                                    self.players[0].used_phys += 1
                    else:
                        ## If we're frozen or spinning out, allow player to shake out of it
                        if e.key in [pygame.K_z, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                            if self.players[0].no_control > 0:
                                self.players[0].no_control -= 0.1
                                self.players[0].shake = True
                            if self.players[0].frozen > 0:
                                self.players[0].frozen -= 0.1
                                self.players[0].shake = True

        return False ## Default return, we have not exited the game yet

    def _quit(self):
        ## Save options to file and quit safely
        self.write_options()
        pygame.quit()
        raise SystemExit

    def increase(self, start, increment, maximum):
        ## Method that increases a value but restricts to the interval [0,maximum]
        return max(0, min(maximum, start + increment))

    def accelerate(self, speed, accel, dt):
        ## Method that accelerates according to dt
        return speed + accel * dt

    def limit(self, value, minimum, maximum):
        ## Method that restricts a value to an interval [minimum, maximum]
        return max(minimum, min(value, maximum))

    def rot_center(self, image, rect, angle):
        ## Method that rotates an image about its center; used for fireball effect
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image, rot_rect

    def project(self, p, camera_x, camera_y, camera_z, camera_depth, width, height, road_width):
        ## Method that projects XY coordinates in the Z direction
        temp_cam_x = (p.x or 0) - camera_x
        temp_cam_y = (p.y or 0) - camera_y
        temp_cam_z = (p.z or 0) - camera_z
        temp_scr_scale = camera_depth / max(1,temp_cam_z+1)
        temp_scr_x = round((width/2) + (temp_scr_scale * temp_cam_x * width / 2))
        temp_scr_y = round((height/2) - (temp_scr_scale * temp_cam_y * height / 2))
        temp_scr_w = round((temp_scr_scale * road_width * width / 2))

        temp_cam = self.Camera(temp_cam_x, temp_cam_y, temp_cam_z)
        temp_scr = self.Screen(temp_scr_scale,
                               temp_scr_x,
                               temp_scr_y,
                               temp_scr_w)
        ## We are manipulating a namedtuple, so we use the _replace method.
        return p._replace(camera=temp_cam, screen=temp_scr)

    def add_segment(self, curve, y):
        ## Method that adds a segment to the road. The road is defined in discrete strips called segments,
        ## which each have a curve, color, and position.
        n = len(self.segments)
        temp_camera_1 = self.Camera(1,1,1)
        temp_camera_2 = self.Camera(1,1,1)
        temp_screen_1 = self.Screen(1,1,1,1)
        temp_screen_2 = self.Screen(1,1,1,1)
        temp_world_1 = self.World(1, self.last_y(), n*self.segment_length, temp_camera_1, temp_screen_1)
        temp_world_2 = self.World(1, y, (n+1)*self.segment_length, temp_camera_2, temp_screen_2)
        temp_color = self.current_course.dark_colors if math.floor(n/self.rumble_length)%2 else self.current_course.light_colors

        temp = self.Segment(n, temp_world_1, temp_world_2, curve, temp_color, [])
        self.segments.append(temp)

    def ease_in(self,a,b,percent):
        ## Eases into a curve for road geometry
        return a + (b-a)*math.pow(percent, 2)

    def ease_out(self,a,b,percent):
        ## Eases out of a curve for road geometry
        return a + (b-a)*(1-math.pow(1-percent, 2))

    def ease_in_out(self,a,b,percent):
        ## Does both
        return a + (b-a) * ((-1*math.cos(percent*3.14159)/2)+0.5)

    def last_y(self):
        ## Gets last y value; only useful for height modulation, which we don't really use... Yet.
        return 0 if len(self.segments) == 0 else self.segments[len(self.segments)-1].p2.y

    def reset_cars(self):
        ## Reset the racers according to which segment they're entering
        for n in range(len(self.players)):
            segment = self.find_segment(self.players[n].position)
            segment.cars.append(self.players[n])

    def add_item(self, num, zpos, xpos, speed, owner, level=0):
        ## Add an item into the field
        if num == 0:
            ## If it's a mystery tarot card, set it with these constants
            temp = self.Item(0,0,0,1573,[xpos,zpos,0])
        else:
            ## Otherwise it's a fireball or ice chunk
            temp = self.Item(num,level,speed,owner,[xpos,zpos,10])
        self.items.append(temp)

    def add_road(self, enter, hold, leave, curve, y):
        start_y = self.last_y()
        end_y = start_y + int(y) * self.segment_length
        n = enter + hold + leave
        total = enter + hold + leave

        for n in range(enter):
            self.add_segment(self.ease_in(0, curve, n/float(enter)), self.ease_in_out(start_y, end_y, n/float(total)))
        for n in range(hold):
            self.add_segment(curve, self.ease_in_out(start_y, end_y, (enter+n)/float(total)))
        for n in range(leave):
            self.add_segment(self.ease_in_out(curve, 0, n/float(leave)), self.ease_in_out(start_y, end_y, (enter+hold+n)/float(total)))

    def add_straight(self, num=None):
        num = num or ROAD.LENGTH.MEDIUM
        self.add_road(num, num, num, 0, 0)

    def add_hill(self, num=None, height=None):
        num = num or ROAD.LENGTH.MEDIUM
        height = height or ROAD.HILL.MEDIUM
        self.add_road(num, num, num, 0, height)

    def add_curve(self, num=None, curve=None, height=None):
        num = num or ROAD.LENGTH.MEDIUM
        curve = curve or ROAD.CURVE.MEDIUM
        height = height or ROAD.HILL.NONE
        self.add_road(num, num, num, curve, height)

    def add_low_rolling_hills(self, num=None, height=None):
        num = num or ROAD.LENGTH.SHORT
        height = height or ROAD.HILL.LOW
        self.add_road(num, num, num, 0, height/2)
        self.add_road(num, num, num, 0, -1*height)
        self.add_road(num, num, num, ROAD.CURVE.EASY, height)
        self.add_road(num, num, num, 0, 0)
        self.add_road(num, num, num, -1*ROAD.CURVE.EASY, height/2)
        self.add_road(num, num, num, 0, 0)

    def add_s_curves(self, num):
        curve = random.choice((ROAD.CURVE.MEDIUM, ROAD.CURVE.HARD))
        self.add_road(num, num, num, -curve, ROAD.HILL.NONE)
        self.add_road(num, num, num, curve, ROAD.HILL.NONE)

    def add_bumps(self):
        self.add_road(10,10,10,0,5)
        self.add_road(10,10,10,0,-2)
        self.add_road(10,10,10,0,-5)
        self.add_road(10,10,10,0,8)
        self.add_road(10,10,10,0,5)

    def add_downhill_to_end(self,num=None):
        num = num or 200
        self.add_road(num,num,num,0, -1 * self.last_y() / self.segment_length)

    def reset_road(self, is_title, course):
        self.segments = []
        self.items = []

        self.current_course = Course(course)

        for num in self.current_course.geometry:
            curve = random.choice((ROAD.CURVE.MEDIUM, ROAD.CURVE.HARD))
            if num == 0:
                self.add_straight(30)
            elif num == 1:
                self.add_s_curves(30)
            elif num == 2:
                self.add_curve(30,-curve)
            elif num == 3:
                self.add_curve(30,curve)

        self.track_length = len(self.segments) * self.segment_length

        if not is_title:
            self.add_item(0,self.track_length/16,-0.8,0,0)
            self.add_item(0,self.track_length/16,0.8,0,0)
            self.add_item(0,self.track_length/16,0,0,0)
            self.add_item(0,self.track_length/16,-0.4,0,0)
            self.add_item(0,self.track_length/16,0.4,0,0)
            self.add_item(0,self.track_length*9/16,-0.8,0,0)
            self.add_item(0,self.track_length*9/16,0.8,0,0)
            self.add_item(0,self.track_length*9/16,0,0,0)
            self.add_item(0,self.track_length*9/16,0.4,0,0)
            self.add_item(0,self.track_length*9/16,-0.4,0,0)

            self.add_item(0,self.track_length*6/16,-0.8,0,0)
            self.add_item(0,self.track_length*6/16,0.8,0,0)
            self.add_item(0,self.track_length*6/16,0,0,0)
            self.add_item(0,self.track_length*6/16,-0.4,0,0)
            self.add_item(0,self.track_length*6/16,0.4,0,0)

            self.add_item(0,self.track_length*12/16,-0.8,0,0)
            self.add_item(0,self.track_length*12/16,0.8,0,0)
            self.add_item(0,self.track_length*12/16,0,0,0)
            self.add_item(0,self.track_length*12/16,-0.4,0,0)
            self.add_item(0,self.track_length*12/16,0.4,0,0)

        self.reset_cars()

        self.segments[0] = self.segments[0]._replace(color = self.current_course.finish)
        self.segments[1] = self.segments[1]._replace(color = self.current_course.start)


    def percent_remaining(self, n, total):
        return (n%total) / total

    def interpolate(self, a, b, percent):
        return a + (b-a)*percent

    def find_segment(self,z):
        return self.segments[int(math.floor(z/self.segment_length) % len(self.segments))]

    def exponential_fog(self, distance, density):
        return 1 / math.pow(math.e, distance*distance*density)

    def render(self, is_done, course, is_title=False):
        ## Player 1 screen
        count = 0
        for screen in self.subscreens:

            base_segment = self.find_segment(self.players[count].position)
            base_index = self.segments.index(base_segment)
            max_y = self.height
            base_percent = self.percent_remaining(self.players[count].position, self.segment_length)
            player_segment = self.find_segment(self.players[count].position + self.players[count].player_z)
            player_percent = self.percent_remaining(self.players[count].position + self.players[count].player_z, self.segment_length)
            player_y = self.interpolate(player_segment.p1.y, player_segment.p2.y, player_percent)
            temp_cam_height = self.camera_height + self.players[count].player_y * self.players[count].player_y / 2.5
            self.players[count].player_z = temp_cam_height * self.players[count].camera_depth

            x = 0
            dx = -1 * base_segment.curve * base_percent

            clip = []

            self.bg_top.fill(self.current_course.light_colors[-1])
            screen.blit(self.bg_top, (0,0))
            self.bg_mid.fill(self.current_course.dark_colors[4])
            screen.blit(self.bg_mid, (0,self.height/3+29))
            self.bg_bot.fill(self.current_course.dark_colors[1])
            screen.blit(self.bg_bot, (0,self.height/3+13+self.height*3/20))
            screen.lock()

            for n in range(self.draw_distance):
                temp_ind = (base_index + n) % len(self.segments)
                looped = temp_ind < base_index
                clip.append(max_y)

                temp_p1 = self.project(self.segments[temp_ind].p1, (self.players[count].player_x * self.road_width) - x,
                             temp_cam_height + player_y, self.players[count].position - (self.track_length if looped else 0),
                             self.players[count].camera_depth, self.width,
                             self.height, self.road_width)
                temp_p2 = self.project(self.segments[temp_ind].p2, (self.players[count].player_x * self.road_width) - x - dx,
                             temp_cam_height + player_y, self.players[count].position  - (self.track_length if looped else 0),
                             self.players[count].camera_depth, self.width,
                             self.height, self.road_width)

                self.segments[temp_ind] = self.segments[temp_ind]._replace(p1=temp_p1, p2=temp_p2)

                x += dx
                dx += self.segments[temp_ind].curve

                if ((self.segments[temp_ind].p1.camera.z <= self.players[count].camera_depth) or\
                    (self.segments[temp_ind].p2.screen.y >= max_y) or\
                    (self.segments[temp_ind].p2.screen.y >= self.segments[temp_ind].p1.screen.y)):
                    continue

                render_segment(screen, self.width, self.lanes,
                               self.segments[temp_ind].p1.screen.x,
                               self.segments[temp_ind].p1.screen.y,
                               self.segments[temp_ind].p1.screen.w,
                               self.segments[temp_ind].p2.screen.x,
                               self.segments[temp_ind].p2.screen.y,
                               self.segments[temp_ind].p2.screen.w,
                               self.segments[temp_ind//self.current_course.road].color)

                max_y = self.segments[temp_ind].p2.screen.y

            for n in range(self.draw_distance-1,0,-1):
                temp_ind = (base_index + n) % len(self.segments)

                render_wall(screen, self.width, self.lanes,
                            self.segments[temp_ind].p1.screen.x,
                            min(clip[n],self.segments[temp_ind].p1.screen.y),
                            self.segments[temp_ind].p1.screen.w,
                            self.segments[temp_ind].p2.screen.x,
                            min(clip[n],self.segments[temp_ind].p2.screen.y),
                            self.segments[temp_ind].p2.screen.w,
                            n, self.draw_distance, self.segments[temp_ind//self.current_course.strip].color,
                            self.current_course.dark_colors)

            screen.unlock()

            for n in range(self.draw_distance-1, -5, -1):
                temp_ind = (base_index + n) % len(self.segments)
                segment = self.segments[temp_ind]

                for i in range(len(self.items)):
                    temp_seg = self.find_segment(self.items[i].xzd[1])
                    if self.items[i].num == 0:
                        if n >= 2 and temp_seg == segment:
                            if self.mystery_width <= 0:
                                sprite = pygame.transform.flip(self.item_img[0], True, False)
                                sprite = pygame.transform.scale(sprite, (int(abs(self.mystery_width)), 64))
                            else:
                                sprite = pygame.transform.scale(self.item_img[0], (int(self.mystery_width), 64))
                            percent = self.percent_remaining(self.items[i].xzd[1], self.segment_length)
                            sprite_scale = self.interpolate(segment.p1.screen.scale, segment.p2.screen.scale, percent)
                            sprite_x = self.interpolate(segment.p1.screen.x, segment.p2.screen.x, percent) + (sprite_scale * self.items[i].xzd[0] * self.road_width * self.width / 2)
                            sprite_y = self.interpolate(segment.p1.screen.y, segment.p2.screen.y, percent)
                            render_sprite(screen, self.width, self.height, self.resolution,
                                          self.road_width, sprite, sprite_scale,
                                          sprite_x, sprite_y, -0.5, -1, clip[n], is_item=True)
                    elif self.items[i].num == 8:
                        if temp_seg == segment:
                            sprite = self.rot_center(self.item_img[8], self.item_img[0].get_rect(), self.fire_rot)[0]
                            percent = self.percent_remaining(self.items[i].xzd[1], self.segment_length)
                            sprite_scale = self.interpolate(segment.p1.screen.scale, segment.p2.screen.scale, percent)
                            sprite_x = self.interpolate(segment.p1.screen.x, segment.p2.screen.x, percent) + (sprite_scale * self.items[i].xzd[0] * self.road_width * self.width / 2)
                            sprite_y = self.interpolate(segment.p1.screen.y, segment.p2.screen.y, percent)
                            render_sprite(screen, self.width, self.height, self.resolution,
                                          self.road_width, sprite, sprite_scale,
                                          sprite_x, sprite_y, -0.5, -1, clip[n], is_item=True)

                    else:
                        if temp_seg == segment:
                            sprite = self.item_img[self.items[i].num]
                            percent = self.percent_remaining(self.items[i].xzd[1], self.segment_length)
                            sprite_scale = self.interpolate(segment.p1.screen.scale, segment.p2.screen.scale, percent)
                            sprite_x = self.interpolate(segment.p1.screen.x, segment.p2.screen.x, percent) + (sprite_scale * self.items[i].xzd[0] * self.road_width * self.width / 2)
                            sprite_y = self.interpolate(segment.p1.screen.y, segment.p2.screen.y, percent)
                            render_sprite(screen, self.width, self.height, self.resolution,
                                          self.road_width, sprite, sprite_scale,
                                          sprite_x, sprite_y, -0.5, -1, clip[n], is_item=True)

            self.hama_mask.set_alpha(min(150,self.players[count].hama_alpha))
            self.mudo_mask.set_alpha(min(150,self.players[count].mudo_alpha))
            screen.blit(self.mudo_mask, (0,0))
            screen.blit(self.hama_mask, (0,0))

            if self.players[count].mudo_cast:
                self.players[count].mudo_cast_alpha += 5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                self.mudo_mask.set_alpha(min(128,self.players[count].mudo_cast_alpha))
                if self.players[count].mudo_cast_alpha >= 512:
                    self.players[count].mudo_cast = False
                screen.blit(self.mudo_mask, (0,0))
            elif self.players[count].mudo_cast_alpha > 0:
                self.players[count].mudo_cast_alpha -= 5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                self.mudo_mask.set_alpha(min(128,self.players[count].mudo_cast_alpha))
                screen.blit(self.mudo_mask, (0,0))

            if self.players[count].hama_cast:
                self.players[count].hama_cast_alpha += 5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                self.hama_mask.set_alpha(min(128,self.players[count].hama_cast_alpha))
                if self.players[count].hama_cast_alpha >= 512:
                    self.players[count].hama_cast = False
                screen.blit(self.hama_mask, (0,0))
            elif self.players[count].hama_cast_alpha > 0:
                self.players[count].hama_cast_alpha -= 5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                self.hama_mask.set_alpha(min(128,self.players[count].hama_cast_alpha))
                screen.blit(self.hama_mask, (0,0))

            ## Render the HUD

            if not is_title:

                for n in range(self.draw_distance-1, -5, -1):
                    temp_ind = (base_index + n) % len(self.segments)
                    next_temp_ind = min(len(self.segments)-1,(base_index + n + 6) % len(self.segments))
                    segment = self.segments[temp_ind]
                    for i in range(len(segment.cars)):
                        car = segment.cars[i]
                        next_temp_segment = self.segments[next_temp_ind]
                        sprite = car.sprite
                        temp_lightning = None
                        if not (-0.1 < car.lightning < 0.1):
                            temp_lightning = self.lightning_img[int(car.lightning * 10) % 2]
                        percent = self.percent_remaining(car.position, self.segment_length)
                        sprite_scale = self.interpolate(next_temp_segment.p1.screen.scale, next_temp_segment.p2.screen.scale, percent)
                        sprite_scale_x = self.interpolate(next_temp_segment.p1.screen.scale, next_temp_segment.p2.screen.scale, percent)
                        temp_y = car.player_y*sprite_scale*7000
                        sprite_x = self.interpolate(next_temp_segment.p1.screen.x, next_temp_segment.p2.screen.x, percent) + (sprite_scale_x * car.player_x * self.road_width * self.width / 2)
                        sprite_y = self.interpolate(next_temp_segment.p1.screen.y-temp_y, next_temp_segment.p2.screen.y-temp_y, percent)
                        shadow_y = self.interpolate(next_temp_segment.p1.screen.y, next_temp_segment.p2.screen.y, percent)
                        render_cpu(screen, car, self.width, self.height, self.resolution, self.road_width,
                                   percent, sprite_scale, sprite_x, sprite_y,
                                   car.speed * (-1 if car.inputs[0] else (1 if car.inputs[1] else 0)),
                                   self.item_img[car.item] if (car.item != None and car.id!=self.players[count].id) else None,
                                   temp_lightning, self.shadow, shadow_y)

                temp_bar_1 = self.bar_3.subsurface(0,0, int(self.bar_3.get_width() * self.players[count].display_health / self.players[count].max_health), self.bar_3.get_height())
                temp_bar_2 = self.bar_1.subsurface(0,0, int(self.bar_1.get_width() * self.players[count].health / self.players[count].max_health), self.bar_1.get_height())
                screen.blit(self.bar_2, (19,17))
                screen.blit(temp_bar_1, (13,11))
                screen.blit(temp_bar_2, (13,11))

                self.health_text.update("%04d/%04d" %(self.players[count].display_health, int(self.players[count].max_health)), (19,48))
                self.health_text.draw(screen)

                if self.players[count].item != None:
                    screen.blit(self.item_img[self.players[count].item], self.item_img[self.players[count].item].get_rect(bottomright=(360*2+8*2,240*2+8*2)))

                if self.players[count].place == 1:
                    screen.blit(self.place_1, (2,480-128))
                elif self.players[count].place == 2:
                    screen.blit(self.place_2, (2,480-128))
                elif self.players[count].place == 3:
                    screen.blit(self.place_3, (2,480-128))
                elif self.players[count].place == 4:
                    screen.blit(self.place_4, (2,480-128))
                elif self.players[count].place == 5:
                    screen.blit(self.place_5, (2,480-128))
                elif self.players[count].place == 6:
                    screen.blit(self.place_6, (2,480-128))

                for item in self.items:
                    if item.num != 0:
                        self.arrow_tick += 1
                        if self.arrow_tick > 99:
                            self.arrow_tick = 0
                        if 0 < (self.players[i].position - item.xzd[1]) / self.segment_length < 300:
                            if self.arrow_tick % 15 not in [0,1,2,3,4,5,6]:
                                screen.blit(self.red_arrow, self.red_arrow.get_rect(midtop=(int((6 + item.xzd[0]*2 - self.players[i].player_x)*self.road_width/24), 480-80)))
                            else:
                                screen.blit(self.yellow_arrow, self.yellow_arrow.get_rect(midtop=(int((6 + item.xzd[0]*2 - self.players[i].player_x)*self.road_width/24), 480-80)))
                            self.item_text.update("%dm" %((self.players[i].position - item.xzd[1]) / self.segment_length),
                                                  center=(int((6 + item.xzd[0]*2 - self.players[i].player_x)*self.road_width/24), 480-48),
                                                  antialiased=False)
                            self.item_text.draw(screen)
                        elif self.players[i].position / self.segment_length < 300 and (item.xzd[1] - self.track_length) / self.segment_length > 300:
                            if self.arrow_tick % 15 not in [0,1,2,3,4,5,6]:
                                screen.blit(self.red_arrow, self.red_arrow.get_rect(midtop=(int((6 + item.xzd[0]*2 - self.players[i].player_x)*self.road_width/24), 480-80)))
                            else:
                                screen.blit(self.yellow_arrow, self.yellow_arrow.get_rect(midtop=(int((6 + item.xzd[0]*2 - self.players[i].player_x)*self.road_width/24), 480-80)))
                            self.item_text.update("%dm" %(((item.xzd[1] - self.track_length) - self.players[i].position) / self.segment_length),
                                                  center=(int((6 + item.xzd[0]*2 - self.players[i].player_x)*self.road_width/24), 480-48),
                                                  antialiased=False)
                            self.item_text.draw(screen)

                #screen.blit(self.persona_img[self.players[count].p_index], self.persona_img[self.players[count].p_index].get_rect(topright=(360*2,0)))
                screen.blit(self.overlay, self.overlay.get_rect(topright=(360*2,0)))

                if self.players[count].lap_text_draw % 15 not in [0,1,2,3,4,5] or self.players[count].lap_text_draw >= 120:
                    screen.blit(self.lap_img[min(4,self.players[count].laps*2-2)], (720-300,0))
                else:
                    screen.blit(self.lap_img[min(5,self.players[count].laps*2-1)], (720-300,0))

                if self.players[count].laps == self.max_laps:
                    if not is_done:
                        self.win_text[6].update("Waiting...")
                        self.win_text[6].draw(screen)
                    else:
                        if not self.has_changed_music and self.music_index == 0 and not self.pause:
                            pygame.mixer.music.load("res/sound/bgm03.ogg")
                            pygame.mixer.music.set_volume(0.5)
                            pygame.mixer.music.play(-1)
                            self.has_changed_music = True

                        for i in range(len(self.players)):
                            if self.players[i].place == 1:
                                self.win_text[0].update("1st : %s" %self.players[i].name, color=[254,208,0] if i == 0 else [255,255,255])
                            elif self.players[i].place == 2:
                                self.win_text[1].update("2nd : %s" %self.players[i].name, color=[254,208,0] if i == 0 else [255,255,255])
                            elif self.players[i].place == 3:
                                self.win_text[2].update("3rd : %s" %self.players[i].name, color=[254,208,0] if i == 0 else [255,255,255])
                            elif self.players[i].place == 4:
                                self.win_text[3].update("4th : %s" %self.players[i].name, color=[254,208,0] if i == 0 else [255,255,255])
                            elif self.players[i].place == 5:
                                self.win_text[4].update("5th : %s" %self.players[i].name, color=[254,208,0] if i == 0 else [255,255,255])
                            elif self.players[i].place == 6:
                                self.win_text[5].update("6th : %s" %self.players[i].name, color=[254,208,0] if i == 0 else [255,255,255])
                            self.win_text[i].draw(screen)

                    self.win_text[7].update("Press ESC / Pause to quit.", center=(360,36*9+2), color=[255,255,255])
                    self.win_text[7].draw(screen)

                if (self.countdown/1000)%60 < 3:
                    if (self.countdown/1000)%60 - 1 < 0.03:
                        self.countdown_text.update("3", center=(360,60))
                    elif (self.countdown/1000)%60 - 2 < 0.03:
                        self.countdown_text.update("2", center=(360,60))
                    elif (self.countdown/1000)%60 - 3 < 0.03:
                        self.countdown_text.update("1", center=(360,60))
                    self.countdown_text.draw(screen)

                if self.screen_index == 1:
                    pygame.transform.smoothscale(screen,self.full_res,self.screen)
                else:
                    self.screen.blit(screen, (0,0))
            count += 1

        if not is_title:
            if self.pause:
                self.pause_subscreen.fill((0,0,0))
                self.pause_text_1.update("Resume Race", center=(180*2,108*2+36), color=[255,255,255] if self.pause_index == 0 else [82,82,82])
                self.pause_text_2.update("To Title", center=(180*2,108*2+36*2), color=[255,255,255] if self.pause_index == 1 else [82,82,82])
                self.pause_text_3.update("Paused", center=(180*2,108*2-36), color=[255,255,255])
                self.pause_text_1.draw(self.pause_subscreen)
                self.pause_text_2.draw(self.pause_subscreen)
                self.pause_text_3.draw(self.pause_subscreen)
                if self.screen_index == 1:
                    pygame.transform.smoothscale(self.pause_subscreen,self.full_res,self.screen)
                else:
                    self.screen.blit(self.pause_subscreen, (0,0))

            if (self.countdown/1000)%60 < 3:
                if self.sound_index == 0:
                    if -0.05 < (self.countdown/1000)%60 < 0.05 or\
                       -0.05 < (self.countdown/1000)%60 - 1 < 0.0 or\
                       -0.05 < (self.countdown/1000)%60 - 2 < 0.0:
                        self.countdown_start.stop()
                        self.countdown_start.play()
                    elif -0.05 < (self.countdown/1000)%60 - 3 < 0.05:
                        self.countdown_end.play()

        pygame.display.flip()

    def update_items(self, dt):
        if self.mystery_width_increase:
            self.mystery_width += 4 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
            if self.mystery_width >= 64:
                self.mystery_width_increase = False
        else:
            self.mystery_width -= 4 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
            if self.mystery_width <= -64:
                self.mystery_width_increase = True

        self.fire_rot += 10.0 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
        if self.fire_rot >= 360:
            self.fire_rot = 0

        for item in self.items:
            for i in range(len(self.players)):
                if item.owner != i and abs(self.players[i].position - item.xzd[1]) < abs(dt * self.players[i].speed - dt * item.speed) and\
                   abs(self.players[i].player_x - item.xzd[0]) <= 0.48 and self.players[i].laps != self.max_laps:
                    if self.players[i].player_y <= 0:
                        if item.num == 0:
                             if self.players[i].item == None:
                                self.players[i].item_scrolling = 2.5
                        elif not self.players[i].recover:
                            self.players[i].item_hit += 1
                            ## Fireball
                            if item.num == 8:
                                if self.sound_index == 0:
                                    self.stop_all_sounds()
                                    self.players[i].flame.play()
                                    if random.randint(1,3) == 1 and self.sound_index == 0:
                                        if self.players[i].voice_hit[self.players[i].voice_index].get_num_channels() == 0:
                                            self.players[i].voice_hit[self.players[i].voice_index].play()
                                            self.players[i].voice_index = 1 if self.players[i].voice_index == 0 else 0
                                self.players[i].flying = True
                                self.players[i].health -= 100
                                self.players[i].no_control += item.level/4.0 + (self.players[i].position + ((self.players[i].laps - 1) * self.track_length)) / self.track_length * 0.6
                            else: ## Ice attack
                                if self.sound_index == 0:
                                    self.stop_all_sounds()
                                    self.players[i].crash.play()
                                    if random.randint(1,3) == 1 and self.sound_index == 0:
                                        if self.players[i].voice_hit[self.players[i].voice_index].get_num_channels() == 0:
                                            self.players[i].voice_hit[self.players[i].voice_index].play()
                                            self.players[i].voice_index = 1 if self.players[i].voice_index == 0 else 0
                                self.players[i].flying = True
                                self.players[i].health -= 50
                                self.players[i].frozen = item.level - 1 + (self.players[i].position + ((self.players[i].laps - 1) * self.track_length)) / self.track_length * 0.8

            item.xzd[1] = self.increase(item.xzd[1], dt * item.speed * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0), self.track_length)
            if item.xzd[1] >= self.track_length:
                item.xzd[1] -= self.track_length
            new_segment = self.find_segment(item.xzd[1])
            #item.xzd[0] = self.limit(item.xzd[0], -2, 2)
            if item.num != 0:
                item.xzd[2] -= dt * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                if item.xzd[2] <= 0:
                    self.items.remove(item)

    def get_new_lap(self, first, is_title=False):
        for p in range(len(self.players)):
            if self.players[p].position >= self.track_length:
                self.players[p].position -= self.track_length
                ## Get a new lap
                if not is_title:
                    self.players[p].laps += 1
                    if self.players[p].laps < self.max_laps:
                        self.players[p].lap_text_draw = 0

            elif first:
                self.players[p].laps += 1
                self.players[p].lap_text_draw = 0

    def update_places(self):
        relative_pos = []
        for i in range(len(self.players)):
            temp = self.players[i].position + self.players[i].laps * self.track_length
            relative_pos.append([temp,i])

        for i in range(len(self.players)):
            if self.players[i].laps == self.max_laps:
                relative_pos[i][0] += (6-self.players[i].place) * self.track_length

        relative_pos.sort(key=lambda x:x[0])

        for i in range(len(self.players)):
            self.players[relative_pos[i][1]].place = len(self.players)-i

    def stop_all_sounds(self):
        for n in range(len(self.players)):
            try:
                self.players[n].engine01.stop()
                self.players[n].engine02.stop()
                self.players[n].engine03.stop()
                self.players[n].thunder.stop()
                self.players[n].whoosh.stop()
                self.players[n].whoosh_long.stop()
                self.players[n].crash.stop()
                self.players[n].flame.stop()
                self.players[n].damage.stop()
            except:
                pass

    def update(self, dt, is_title=False):
        if not self.pause:
            is_done = True
            self.update_items(dt)
            first_pos = 0

            for p in range(len(self.players)):

                first_pos = 0
                is_player_done = False

                for q in range(len(self.players)):
                    if p != q and self.players[q].place == 1:
                        first_pos = self.players[q].position + (self.players[q].laps-1) * self.track_length

                    if self.players[q].laps != self.max_laps:
                        is_done = False

                if self.players[p].laps == self.max_laps:
                    is_player_done = True
                    self.players[p].item = None
                    self.players[p].item_scrolling = 0

                if self.players[p].lap_text_draw < 120:
                    self.players[p].lap_text_draw += 1

                if self.players[p].boost_diff > self.players[p].threshold:
                    if random.randint(0,self.players[p].has_boosted+1) <= 50:
                        self.players[p].has_boosted += 1
                        if self.sound_index == 0:
                            self.stop_all_sounds()
                            self.players[p].whoosh_long.play()
                            if self.players[p].voice_speed[self.players[p].voice_index].get_num_channels() == 0:
                                self.players[p].voice_speed[self.players[p].voice_index].play()
                                self.players[p].voice_index = 1 if self.players[p].voice_index == 0 else 0
                        self.players[p].speed_up = 0.6
                        self.players[p].speed = self.max_speed * 1.2
                        self.players[p].boost = -1 * self.players[p].boost_diff
                        self.players[p].boost_diff = 0.0
                    else:
                        self.players[p].no_control += self.players[p].boost_diff/10
                        self.players[p].boost = -2 * self.players[p].boost_diff
                        self.players[p].boost_diff = 0.0

                if self.players[p].flying == True:
                    self.players[p].player_y += 6 + self.gravity * self.players[p].accumulator * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    self.players[p].accumulator += 1 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    if self.players[p].player_y <= 0:
                        self.players[p].player_y = 0
                        self.players[p].accumulator = 0
                        self.players[p].flying = False

                if self.players[p].no_control > 0:
                    self.players[p].no_control -= dt * self.players[p].recovery * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

                if self.players[p].attack > 0:
                    self.players[p].attack -= 8
                    if self.players[p].attack < 0:
                        self.players[p].attack = 0
                    for q in range(len(self.players)):
                        if q != p and abs(self.players[p].position - self.players[q].position) < self.segment_length * 3 and\
                           abs(self.players[p].player_x - self.players[q].player_x) <= 0.75 and not self.players[q].recover:
                            if self.sound_index == 0:
                                self.stop_all_sounds()
                                self.players[q].damage.play()
                            self.players[q].no_control += 0.2
                            self.players[q].flying = True
                            self.players[q].item_hit += 1
                            self.players[q].health -= int(10 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))

                if self.players[p].health < 0:
                    self.players[p].health = 0

                if self.players[p].display_health <= 0:
                    self.players[p].no_control += 1.5
                    self.players[p].flying = True
                    self.players[p].display_health = int(self.players[p].max_health)
                    self.players[p].recover = True
    
                if self.players[p].health < self.players[p].display_health:
                    if self.players[p].recover:
                        self.players[p].health = int(self.players[p].health + 3 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))
                        if self.players[p].health >= int(self.players[p].max_health):
                            self.players[p].health = int(self.players[p].max_health)
                            self.players[p].recover = False
                    else:
                        self.players[p].display_health -= int(5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))

                if self.players[p].frozen > 0:
                    self.players[p].frozen -= dt * self.players[p].recovery * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

                if self.players[p].mudo:
                    self.players[p].mudo_alpha += 5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    if self.players[p].mudo_alpha >= 512:
                        self.players[p].mudo = False
                elif self.players[p].mudo_alpha > 0:
                    self.players[p].mudo_alpha -= 5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

                if self.players[p].hama:
                    self.players[p].hama_alpha += 5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    if self.players[p].hama_alpha >= 512:
                        self.players[p].hama = False
                elif self.players[p].hama_alpha > 0:
                    self.players[p].hama_alpha -= 5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

                if self.players[p].item_scrolling > 0:
                    if p == 0 and self.sound_index == 0:
                        #self.stop_all_sounds()
                        self.scroll_sound.play()
                    self.players[p].item_scrolling -= dt * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    self.players[p].item = random.choice(self.players[p].item_choice)

                if self.players[p].lightning > 0:
                    self.players[p].lightning -= dt * self.players[p].recovery * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                elif self.players[p].lightning < 0:
                    self.players[p].lightning += dt * self.players[p].recovery * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

                temp_factor_2 = 1.0 + self.players[p].speed_up*5
                if self.players[p].speed_up > 0:
                    self.players[p].speed_up -= dt * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

                ## Increase forward movement
                start_position = self.players[p].position
                old_segment = self.find_segment(self.players[p].position)

                if old_segment.curve < 0:
                    temp_factor_4 = max((24 - self.players[p].player_x*2) / 24, 1.0)
                elif old_segment.curve > 0:
                    temp_factor_4 = max((24 + self.players[p].player_x*2) / 24, 1.0)
                else:
                    temp_factor_4 = 1.0

                speed_scale = (first_pos - (self.players[p].position+(self.players[p].laps-1)*self.track_length)) / (first_pos+1) + 1.0
                temp_factor_1 = max(1.0, speed_scale)

                self.players[p].position = self.increase(self.players[p].position, dt * self.players[p].speed * temp_factor_4 * temp_factor_1 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0), self.track_length*2)

                new_segment = self.find_segment(self.players[p].position)

                dx = dt * self.players[p].speed / (self.max_speed * self.players[p].max_speed_mod * temp_factor_4 * temp_factor_1) * (3.0 if ((self.players[p].player_x < -1) or (self.players[p].player_x > 1)) else 1.7)

                ## X-axis movement
                if self.players[p].inputs[0]:
                    self.players[p].player_x -= dx * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                elif self.players[p].inputs[1]:
                    self.players[p].player_x += dx * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

                if self.players[p].lightning < -0.1:
                    self.players[p].player_x -= dx * 2.5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                elif self.players[p].lightning > 0.1:
                    self.players[p].player_x += dx * 2.5 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)

                if self.players[p].speed > 0:
                    self.players[p].player_x = self.accelerate(self.players[p].player_x, self.accel * self.players[p].accel_mod * new_segment.curve / float(ROAD.CURVE.HARD) * -1 * self.players[p].speed / (self.max_speed * self.players[p].max_speed_mod) * 0.0005, dt * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))
 
                ## Speed up or slow down
                if is_player_done:
                    self.players[p].speed = self.accelerate(self.players[p].speed, self.braking * self.players[p].braking_mod * 2.5, dt * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))
                elif self.players[p].frozen > 0:
                    self.players[p].speed = self.accelerate(self.players[p].speed, self.braking * self.players[p].braking_mod * 1.0, dt * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))
                elif self.players[p].no_control > 0:
                    self.players[p].speed = self.accelerate(self.players[p].speed, self.decel* self.players[p].decel_mod * 0.4, dt * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))

                if self.players[p].inputs[2]:
                    if self.players[p].no_control <= 0 and self.players[p].frozen <= 0:
                        self.players[p].speed = self.accelerate(self.players[p].speed, self.accel * self.players[p].accel_mod * temp_factor_1, dt * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))
                else:
                    self.players[p].speed = self.accelerate(self.players[p].speed, self.decel * self.players[p].decel_mod, dt * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))

                if (((self.players[p].player_x < -1) or (self.players[p].player_x > 1)) and \
                    (self.players[p].speed > self.offroad_limit * self.players[p].offroad_limit_mod)):
                    self.players[p].speed = self.accelerate(self.players[p].speed, self.offroad_decel * self.players[p].offroad_decel_mod, dt * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))

                self.players[p].player_x = self.limit(self.players[p].player_x, -2.5, 2.5)

                self.players[p].speed = self.limit(self.players[p].speed, 0, self.max_speed * self.players[p].max_speed_mod * temp_factor_2) * random.randint(99,101)/100.0

                self.update_car(self.players[p], old_segment, new_segment)

            if not is_title:
                if self.players[0].laps == self.max_laps and not self.has_written:
                    self.unlocked = self.write_achievements()
                    self.has_written = True
                    if self.music_index == 0:
                        pygame.mixer.music.set_volume(0.25)

                engine_played = False
                for p in range(len(self.players)):
                    meter = 70*self.players[p].speed / (self.max_speed * self.players[p].max_speed_mod)
                    if self.sound_index == 0 and not engine_played:
                        if meter >= 60:
                            if self.players[p].engine01.get_num_channels() > 0:
                                self.players[p].engine01.stop()
                            if self.players[p].engine02.get_num_channels() > 0:
                                self.players[p].engine02.stop()
                            if self.players[p].engine03.get_num_channels() == 0:
                                self.players[p].engine03.play(-1)
                                engine_played = True
                        elif meter >= 30:
                            if self.players[p].engine01.get_num_channels() > 0:
                                self.players[p].engine01.stop()
                            if self.players[p].engine03.get_num_channels() > 0:
                                self.players[p].engine03.stop()
                            if self.players[p].engine02.get_num_channels() == 0:
                                self.players[p].engine02.play(-1)
                                engine_played = True
                        elif meter > 0:
                            if self.players[p].engine03.get_num_channels() > 0:
                                self.players[p].engine03.stop()
                            if self.players[p].engine02.get_num_channels() > 0:
                                self.players[p].engine02.stop()
                            if self.players[p].engine01.get_num_channels() == 0:
                                self.players[p].engine01.play(-1)
                                engine_played = True
                        else:
                            if self.players[p].engine03.get_num_channels() > 0:
                                self.players[p].engine03.stop()
                            if self.players[p].engine02.get_num_channels() > 0:
                                self.players[p].engine02.stop()
                            if self.players[p].engine01.get_num_channels() > 0:
                                self.players[p].engine01.stop()

            self.get_new_lap(False, is_title)

            return is_done

        return False

    def write_achievements(self):

        try:
            f = open("res/data/data.dat", "r+")
            f_text = f.readlines()
            f.seek(0)
            f.flush()

            new_unlock_1 = self.unlocked[0]
            new_unlock_2 = self.unlocked[1]
            new_unlock_3 = self.unlocked[2]
            new_unlock_4 = self.unlocked[3]
            new_unlock_5 = self.unlocked[4]
            new_unlock_6 = self.unlocked[5]
            new_unlock_7 = self.unlocked[6]
            new_unlock_8 = self.unlocked[7]
            new_unlock_9 = self.unlocked[8]
            new_unlock_10 = self.unlocked[9]

            f = open("res/data/data.dat", "r+")

            ## Achievements 0 - Use the same move 5 times or more
            if self.achievements[0] == 0 and self.mode == 7 and self.players[0].health == int(self.players[0].max_health):
                f.write("1\n")
            else:
                f.write(f_text[0])

            ## Achievement 1 - Don"t get hit by items
            if self.achievements[1] == 0 and self.players[0].item_hit == 0 and self.mode == 7:
                f.write("1\n")
            else:
                f.write(f_text[1])

            ## Achievement 2 - First place Yu single player
            if self.achievements[2] == 0 and self.players[0].num == 0 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[2] = 1
                f.write("1\n")
            else:
                f.write(f_text[2])

            ## Achievement 3 - First place Yosuke single player
            if self.achievements[3] == 0 and self.players[0].num == 1 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[3] = 1
                f.write("1\n")
            else:
                f.write(f_text[3])

            ## Achievement 4 - First place Yukiko single player
            if self.achievements[4] == 0 and self.players[0].num == 2 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[4] = 1
                f.write("1\n")
            else:
                f.write(f_text[4])

            ## Achievement 5 - First place Chie single player
            if self.achievements[5] == 0 and self.players[0].num == 3 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[5] = 1
                f.write("1\n")
            else:
                f.write(f_text[5])

            ## Achievement 6 - First place Kanji single player
            if self.achievements[6] == 0 and self.players[0].num == 4 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[6] = 1
                f.write("1\n")
            else:
                f.write(f_text[6])

            ## Achievement 7 - First place Naoto single player
            if self.achievements[7] == 0 and self.players[0].num == 5 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[7] = 1
                f.write("1\n")
            else:
                f.write(f_text[7])

            ## Achievement 8 - First place Teddie single player
            if self.achievements[8] == 0 and self.players[0].num == 6 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[8] = 1
                f.write("1\n")
            else:
                f.write(f_text[8])

            ## Achievement 9 - First place Minato single player
            if self.achievements[9] == 0 and self.players[0].num == 8 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[9] = 1
                f.write("1\n")
            else:
                f.write(f_text[9])


            ## Achievement 10 - First place Yukari single player
            if self.achievements[10] == 0 and self.players[0].num == 9 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[10] = 1
                f.write("1\n")
            else:
                f.write(f_text[10])

            ## Achievement 11 - First place Junpei single player
            if self.achievements[11] == 0 and self.players[0].num == 10 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[11] = 1
                f.write("1\n")
            else:
                f.write(f_text[11])

            ## Achievement 12 - First place Akihiko single player
            if self.achievements[12] == 0 and self.players[0].num == 11 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[12] = 1
                f.write("1\n")
            else:
                f.write(f_text[12])

            ## Achievement 13 - First place Mitsuru single player
            if self.achievements[13] == 0 and self.players[0].num == 12 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[13] = 1
                f.write("1\n")
            else:
                f.write(f_text[13])

            ## Achievement 14 - First place Aigis single player
            if self.achievements[14] == 0 and self.players[0].num == 13 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[14] = 1
                f.write("1\n")
            else:
                f.write(f_text[14])

            ## Achievement 15 - First place Shinjiro single player
            if self.achievements[15] == 0 and self.players[0].num == 14 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[15] = 1
                f.write("1\n")
            else:
                f.write(f_text[15])

            ## Achievement 16 - First place Ken single player
            if self.achievements[16] == 0 and self.players[0].num == 15 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[16] = 1
                f.write("1\n")
            else:
                f.write(f_text[16])

            ## Achievement 17 - Unlock secret character
            if self.achievements[17] == 0:
                if sum(self.achievements[9:17]) == 8:
                    self.achievements[17] = 1
                    new_unlock_1 = True
                    f.write("1\n")
                else:
                    f.write(f_text[17])
            else:
                f.write(f_text[17])

            ## Achievement 18 - Finish under 1:00 single player
            if self.achievements[18] == 0 and self.mode == 7 and int(((self.time/1000)/60)%60) < 1:
                f.write("1\n")
            else:
                f.write(f_text[18])

            ## Achievement 19 - 1 mini-turbos single player
            if self.achievements[19] == 0 and self.mode == 7 and self.players[0].has_boosted >= 1:
                f.write("1\n")
            else:
                f.write(f_text[19])

            ## Achievement 20 - Finish without items single player
            if self.achievements[20] == 0 and self.mode == 7 and self.players[0].health <= int(self.players[0].max_health * 0.10):
                f.write("1\n")
            else:
                f.write(f_text[20])

            ## Achievement 21 - use all items
            if self.achievements[21] == 0 and self.players[0].used_agi > 0 and\
               self.players[0].used_bufu > 0 and\
               self.players[0].used_garu > 0 and\
               self.players[0].used_zio > 0 and\
               self.players[0].used_hama > 0 and\
               self.players[0].used_mudo > 0 and\
               self.players[0].used_phys > 0 and\
               self.mode == 7:
                f.write("1\n")
            else:
                f.write(f_text[21])

            ## Achievement 22 - Unlock secret character
            if self.achievements[22] == 0:
                if sum(self.achievements[2:9]) == 7:
                    self.achievements[22] = 1
                    new_unlock_2 = True
                    f.write("1\n")
                else:
                    f.write(f_text[22])
            else:
                f.write(f_text[22])

            ## Story Mode unlockers
            if self.achievements[23] == 0 and self.players[0].num == 0 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[23] = 1
                f.write("1\n")
                new_unlock_3 = True
            else:
                f.write(f_text[23])

            if self.achievements[24] == 0 and self.players[0].num == 1 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[24] = 1
                f.write("1\n")
                new_unlock_4 = True
            else:
                f.write(f_text[24])

            if self.achievements[25] == 0 and self.players[0].num == 2 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[25] = 1
                f.write("1\n")
                new_unlock_5 = True
            else:
                f.write(f_text[25])

            if self.achievements[26] == 0 and self.players[0].num == 3 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[26] = 1
                f.write("1\n")
                new_unlock_6 = True
            else:
                f.write(f_text[26])

            if self.achievements[27] == 0 and self.players[0].num == 4 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[27] = 1
                f.write("1\n")
                new_unlock_7 = True
            else:
                f.write(f_text[27])

            if self.achievements[28] == 0 and self.players[0].num == 5 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[28] = 1
                f.write("1\n")
                new_unlock_8 = True
            else:
                f.write(f_text[28])

            if self.achievements[29] == 0 and self.players[0].num == 6 and self.mode == 8 and self.players[0].place == 1:
                self.achievements[29] = 1
                f.write("1\n")
                new_unlock_9 = True
            else:
                f.write(f_text[29])

            f.close()

        except (IOError, IndexError, ValueError):
            try:
                os.remove("res/data/data.dat")
            except:
                pass

            new_unlock_1 = self.unlocked[0]
            new_unlock_2 = self.unlocked[1]
            new_unlock_3 = self.unlocked[2]
            new_unlock_4 = self.unlocked[3]
            new_unlock_5 = self.unlocked[4]
            new_unlock_6 = self.unlocked[5]
            new_unlock_7 = self.unlocked[6]
            new_unlock_8 = self.unlocked[7]
            new_unlock_9 = self.unlocked[8]
            new_unlock_10 = self.unlocked[9]

            f = open("res/data/data.dat", "r+")

            ## Achievements 0 - Use the same move 5 times or more
            if self.achievements[0] == 0 and self.mode == 7 and self.players[0].health == int(self.players[0].max_health):
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 1 - Don"t get hit by items
            if self.achievements[1] == 0 and self.players[0].item_hit == 0 and self.mode == 7:
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 2 - First place Yu single player
            if self.achievements[2] == 0 and self.players[0].num == 0 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[2] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 3 - First place Yosuke single player
            if self.achievements[3] == 0 and self.players[0].num == 1 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[3] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 4 - First place Yukiko single player
            if self.achievements[4] == 0 and self.players[0].num == 2 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[4] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 5 - First place Chie single player
            if self.achievements[5] == 0 and self.players[0].num == 3 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[5] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 6 - First place Kanji single player
            if self.achievements[6] == 0 and self.players[0].num == 4 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[6] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 7 - First place Naoto single player
            if self.achievements[7] == 0 and self.players[0].num == 5 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[7] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 8 - First place Teddie single player
            if self.achievements[8] == 0 and self.players[0].num == 6 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[8] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 9 - First place Minato single player
            if self.achievements[9] == 0 and self.players[0].num == 8 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[9] = 1
                f.write("1\n")
            else:
                f.write("0\n")


            ## Achievement 10 - First place Yukari single player
            if self.achievements[10] == 0 and self.players[0].num == 9 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[10] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 11 - First place Junpei single player
            if self.achievements[11] == 0 and self.players[0].num == 10 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[11] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 12 - First place Akihiko single player
            if self.achievements[12] == 0 and self.players[0].num == 11 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[12] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 13 - First place Mitsuru single player
            if self.achievements[13] == 0 and self.players[0].num == 12 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[13] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 14 - First place Aigis single player
            if self.achievements[14] == 0 and self.players[0].num == 13 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[14] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 15 - First place Shinjiro single player
            if self.achievements[15] == 0 and self.players[0].num == 14 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[15] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 16 - First place Ken single player
            if self.achievements[16] == 0 and self.players[0].num == 15 and self.mode == 7 and self.players[0].place <= 3:
                self.achievements[16] = 1
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 17 - Unlock secret character
            if self.achievements[17] == 0:
                if sum(self.achievements[9:17]) == 8:
                    self.achievements[17] = 1
                    new_unlock_1 = True
                    f.write("1\n")
                else:
                    f.write("0\n")
            else:
                f.write("0\n")

            ## Achievement 18 - Finish under 1:00 single player
            if self.achievements[18] == 0 and self.mode == 7 and int(((self.time/1000)/60)%60) < 1:
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 19 - 1 mini-turbos single player
            if self.achievements[19] == 0 and self.mode == 7 and self.players[0].has_boosted >= 1:
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 20 - Finish without items single player
            if self.achievements[20] == 0 and self.mode == 7 and self.players[0].health <= int(self.players[0].max_health * 0.10):
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 21 - use all items
            if self.achievements[21] == 0 and self.players[0].used_agi > 0 and\
               self.players[0].used_bufu > 0 and\
               self.players[0].used_garu > 0 and\
               self.players[0].used_zio > 0 and\
               self.players[0].used_hama > 0 and\
               self.players[0].used_mudo > 0 and\
               self.players[0].used_phys > 0 and\
               self.mode == 7:
                f.write("1\n")
            else:
                f.write("0\n")

            ## Achievement 22 - Unlock secret character
            if self.achievements[22] == 0:
                if sum(self.achievements[2:9]) == 7:
                    self.achievements[22] = 1
                    new_unlock_2 = True
                    f.write("1\n")
                else:
                    f.write("0\n")
            else:
                f.write("0\n")
            ## Story Mode unlockers
            if self.achievements[23] == 0 and self.players[0].num == 0 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[23] = 1
                f.write("1\n")
                new_unlock_3 = True
            else:
                f.write("0\n")

            if self.achievements[24] == 0 and self.players[0].num == 1 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[24] = 1
                f.write("1\n")
                new_unlock_4 = True
            else:
                f.write("0\n")

            if self.achievements[25] == 0 and self.players[0].num == 2 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[25] = 1
                f.write("1\n")
                new_unlock_5 = True
            else:
                f.write("0\n")

            if self.achievements[26] == 0 and self.players[0].num == 3 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[26] = 1
                f.write("1\n")
                new_unlock_6 = True
            else:
                f.write("0\n")

            if self.achievements[27] == 0 and self.players[0].num == 4 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[27] = 1
                f.write("1\n")
                new_unlock_7 = True
            else:
                f.write("0\n")

            if self.achievements[28] == 0 and self.players[0].num == 5 and self.mode == 8 and self.players[0].place <= 3:
                self.achievements[28] = 1
                f.write("1\n")
                new_unlock_8 = True
            else:
                f.write("0\n")

            if self.achievements[29] == 0 and self.players[0].num == 6 and self.mode == 8 and self.players[0].place == 1:
                self.achievements[29] = 1
                f.write("1\n")
                new_unlock_9 = True
            else:
                f.write("0\n")

            f.close()

        return new_unlock_1, new_unlock_2, new_unlock_3, new_unlock_4, new_unlock_5, new_unlock_6, new_unlock_7, new_unlock_8, new_unlock_9, new_unlock_10

    def load_achievements(self):
        self.achievements = [0,0,0,0,0,
                             0,0,0,0,0,
                             0,0,0,0,0,
                             0,0,0,0,0,
                             0,0,0,0,0,
                             0,0,0,0,0,
                             0,0]
        try:
            f = open("res/data/data.dat", "r")
            f_text = f.readlines()
            f.close()
            for n in range(32):
                if int(f_text[n]) == 1:
                    self.achievements[n] = 1
        except (IOError, IndexError, ValueError):
            try:
                os.remove("res/data/data.dat")
            except:
                pass
            f = open("res/data/data.dat", "w")
            for n in range(32):
                f.write("0\n")
            f.close()

    def title(self):
        self.load_achievements()

        running = False
        story_mode = False
        title_text = Text("", (0,0), num=2, border=True)
        ## Normal text
        name_text1 = Text("", (0,0), border=True)
        name_text2 = Text("", (0,0), border=True)
        name_text3 = Text("", (0,0), border=True)
        name_text4 = Text("", (0,0), border=True)
        name_text5 = Text("", (0,0), border=True)
        name_text6 = Text("", (0,0), border=True)
        name_text7 = Text("", (0,0), border=True)
        name_text8 = Text("", (0,0), border=True)
        name_text9 = Text("", (0,0), border=True)
        name_text10 = Text("", (0,0), border=True)
        name_text11 = Text("", (0,0), border=True)
        name_text12 = Text("", (0,0), border=True)
        name_text13 = Text("", (0,0), border=True)
        name_text14 = Text("", (0,0), border=True)
        name_text15 = Text("", (0,0), border=True)
        name_text16 = Text("", (0,0), border=True)
        ## Small text
        text_list = [Text("", (0,0), size=24, border=True) for x in range(13)]
        self.mode = 1

        ## Character information
        story_characters = []
        story_strings = []
        characters = []
        stat_values = []
        persona_names = []  ## Names
        persona_list = []   ## Image reference indices
        persona_skills = [] ## Skill image indices
        persona_stats = []  ## Persona stats

        for i in range(17):
            f = open("res/char/%d.dat" %(i+1), "r").readlines()
            name = "Null"
            temp_stat = [0,0,0,0,0,0]
            temp_persona_list = []
            temp_persona_names = []
            temp_persona_skills = []
            temp_persona_stats = []
            temp_story_strings = []
            for line in f:
                ## Get the name string
                if line.find("STORY:") != -1:
                    for q in range(10):
                        temp_story_strings.append(f[f.index(line)+q+1].replace("\n",""))
                elif line.find("name = ") != -1:
                    name = line.strip("name = ").replace("\n","")
                elif line.find("max_speed = ") != -1:
                    temp_stat[1] = int(line.strip("max_speed = "))
                elif line.find("accel = ") != -1:
                    temp_stat[2] = int(line.strip("accel = "))
                elif line.find("offroad = ") != -1:
                    temp_stat[3] = int(line.strip("offroad = "))
                elif line.find("recovery = ") != -1:
                    temp_stat[4] = int(line.strip("recovery = "))
                elif line.find("threshold = ") != -1:
                    temp_stat[5] = int(line.strip("threshold = "))
                elif line.find("health = ") != -1:
                    temp_stat[0] = int(float(line.strip("health = "))/175)
                elif line.find("persona = ") != -1:
                    temp_persona_list = line.strip("persona = ").split("/")
                    temp_persona_list = [int(item) for item in temp_persona_list]
                    for num in temp_persona_list:
                        g = open("res/persona/p%03d.dat" %num, "r").readlines()
                        temp_name = "Null"
                        temp_skills = []
                        temp_stat_list = [0,0,0,0,0,0]
                        for line in g:
                            if line.find("name = ") != -1:
                                temp_name = line.strip("name = ").replace("\n","")
                            elif line.find("spec = ") != -1:
                                skill_list = line.strip("spec = ").split(",")
                                temp_skills = [int(item) for item in skill_list]
                            elif line.find("max_speed = ") != -1:
                                temp_stat_list[1] = int(line.strip("max_speed = "))
                            elif line.find("accel = ") != -1:
                                temp_stat_list[2] = int(line.strip("accel = "))
                            elif line.find("offroad = ") != -1:
                                temp_stat_list[3] = int(line.strip("offroad = "))
                            elif line.find("recovery = ") != -1:
                                temp_stat_list[4] = int(line.strip("recovery = "))
                            elif line.find("threshold = ") != -1:
                                temp_stat_list[5] = int(line.strip("threshold = "))
                            elif line.find("health = ") != -1:
                                temp_stat_list[0] = int(float(line.strip("health = "))/150)
                        temp_persona_names.append(temp_name)
                        temp_persona_skills.append(temp_skills)
                        temp_persona_stats.append(temp_stat_list)

            characters.append(name)
            story_strings.append(temp_story_strings)
            stat_values.append(temp_stat)
            persona_names.append(temp_persona_names)
            persona_list.append(temp_persona_list)
            persona_skills.append(temp_persona_skills)
            persona_stats.append(temp_persona_stats)

            if i < 7:
                story_characters.append(name)

        if not self.achievements[29]:
            for i in range(8):
                characters[8+i] = None
        if not self.achievements[17]:
            characters[16] = None
        if not self.achievements[22]:
            characters[7] = None

        for i in range(6):
            if not self.achievements[23+i]:
                story_characters[i+1] = None

        stat_strings = ["HEALTH","SPEED","ACCEL","OFFROAD","RECOVERY","TURBO"]
        title_options = ["Free Race Mode","Story Mode","Gamepad","Awards","Options","Quit Game"]
        title_strings = ["Choose Personas and courses!",
                         "Play the game's seven chapters!",
                         "Modify button mappings!",
                         "View unlocked achievements!",
                         "Customize preferences!",
                         "Exit the game client!"]
        option_strings = ["Windowed or maximized.",
                          "Toggle interface effects.",
                          "Toggle background music.",
                          "Toggle sound effects.",
                          "Limit to certain input.",
                          "Change max racer stats.",
                          "Reset to default.",
                          "Return to title."]
        achieve_strings = []
        screen_size = ["Default", "Full"]
        interface = ["Stylish", "Simple"]
        music_toggle = ["On", "Off"]
        sound_toggle = ["On", "Off"]
        colors = [[[0,62,81],[0,87,155]],
                  [[126,112,1],[182,123,0]],
                  [[20,126,0],[0,175,0]],
                  [[81,0,51],[144,0,195]],
                  [[126,0,12],[187,16,0]],
                  [[39,39,39],[77,77,77]],
                  [[255,255,255],[64,64,64]]
                  ]
        old_screen_index = self.screen_index
        setting = False
        racers = None
        car_center = 360

        split = ["Wide","Tall"]
        inputs = ["Off","Keyboard","Gamepad"]

        menu_index = 0

        self.credit_alpha = 0

        self.players = []
        index1 = random.randint(0,6)
        self.players.append(Player(index1,"TITLE", 1, is_title=True))
        course = 11
        self.reset_main(course, is_title=True)

        title_scale = 1.0
        title_shake = 0

        while not running and not story_mode:
            rate = self.clock.tick(self.fps)

            self.rotate_angle += 0.25 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
            if self.rotate_angle > 360:
                self.rotate_angle = 0

            if self.mode in [1,7]:
                self.players[0].inputs[0] = False
                self.players[0].inputs[1] = False

                segment = self.find_segment(self.players[0].position)

                if (segment.curve < 0 and self.players[0].player_x > self.players[0].lane) or\
                   self.players[0].player_x > 1:
                    self.players[0].inputs[0] = True
                    car_center -= 1
                    if car_center < 240:
                        car_center = 240
                elif (segment.curve > 0 and self.players[0].player_x < self.players[0].lane) or\
                     self.players[0].player_x < -1:
                    self.players[0].inputs[1] = True
                    car_center += 1
                    if car_center > 480:
                        car_center = 480

                self.players[0].inputs[2] = True
                self.players[0].speed = self.max_speed * 0.15

                dt = 1.0/rate
                self.update(self.step, is_title=True)
                self.render(False, course, is_title=True)

                if self.mode == 7:
                    self.subscreen1.blit(self.title_back[6], (0,0))
                else:
                    self.subscreen1.blit(self.title_back[menu_index], (0,0))

            else:
                self.subscreen1.fill(colors[menu_index][0])

            if self.mode == 1:
                character_index = 0
                story_index = 0
                old_course = 0
                new_course = 0
                p_index_1 = 0
                option_index = 0
                config_index = 0
                achieve_index = 0
                rendered_awards = False
                shake1 = 96

                if self.interface_index == 0:
                    title_scale += 0.0036 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    if title_scale > 1.0375:
                        temp_scale = 2.075 - title_scale
                    else:
                        temp_scale = title_scale

                    if title_scale > 1.075:
                        title_scale = 1.0

                    if abs(title_shake) > 0:
                        title_shake /= -2

                    temp = pygame.transform.smoothscale(self.title_img, (int(self.title_img.get_width()*temp_scale),
                                                                   int(self.title_img.get_height()*temp_scale)))
                    self.subscreen1.blit(temp, temp.get_rect(center=(200,200)))
                else:
                    title_shake = 0
                    self.subscreen1.blit(self.title_img, self.title_img.get_rect(center=(200,200)))
                

                pygame.draw.rect(self.subscreen1, colors[menu_index][1], (404 if menu_index==0 else (428 if menu_index==1 else 448),28*menu_index+36,720,32))
                for q in range(6):
                    if q == menu_index:
                        name_text1.update(title_options[q], (title_shake,28*q+30+title_shake), color=[255,255,255], right=710)
                        name_text1.draw(self.subscreen1)
                    else:
                        if q > menu_index:
                            text_list[q].update(title_options[q], (0,28*q+36), color=colors[q][1], right=710)
                        else:
                            text_list[q].update(title_options[q], (0,28*q+36), color=colors[q][1], right=710)
                        text_list[q].draw(self.subscreen1)

                text_list[10].update(title_strings[menu_index], pos=(10,36*6+230), color=[255,255,255])
                text_list[10].draw(self.subscreen1)

            elif self.mode == 2:
                self.subscreen1.blit(self.menu_back[0], (0,0))
                temp1 = self.rot_center(self.rotate_img[0], self.rotate_img[0].get_rect(), self.rotate_angle)[0]
                temp2 = self.rot_center(self.rotate_img[5], self.rotate_img[5].get_rect(), self.rotate_angle)[0]
                self.subscreen1.blit(temp1, temp1.get_rect(center=(60,-10)))
                self.subscreen1.blit(temp2, temp2.get_rect(center=(720-60,540)))

                self.icon_subscreen.set_alpha(self.icon_alpha)

                if self.interface_index == 0:
                    if shake1 > 0:
                        shake1 /= int(2 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))
                else:
                    shake1 = 0

                self.subscreen1.blit(pygame.transform.smoothscale(self.persona_img[persona_list[character_index][p_index_1]-1],(60,60)), (380,5*36+86))
                self.subscreen1.blit(self.icon_subscreen, (380, 5*36+86))
                self.subscreen1.blit(self.silhouettes[character_index], self.silhouettes[character_index].get_rect(bottomleft=(-80-shake1,240*2+100)))
                self.subscreen1.blit(self.portraits[character_index], self.portraits[character_index].get_rect(bottomleft=(-80,240*2+100)))

                for count in range(7):
                    if count+1 in persona_skills[character_index][p_index_1]:
                        self.subscreen1.blit(self.small_img[count], (380+64+34*count,5*36+76+34))
                    else:
                        self.subscreen1.blit(self.dark_img[count], (380+64+34*count,5*36+76+34))

                for i in range(6):
                    text_list[i].update(stat_strings[i], color=[255,255,255], pos=(376,i*40+15))
                    text_list[i].draw(self.subscreen1)
                    for j in range(6):
                        if j < (stat_values[character_index][i] - self.engine_class + persona_stats[character_index][p_index_1][i]):
                            pygame.draw.rect(self.subscreen1, (0,0,0), (j*56 + 382, i*40 + 50, 52, 7))
                            pygame.draw.rect(self.subscreen1, (225,236,244), (j*56 + 379, i*40 + 47, 52, 7))
                        else:
                            pygame.draw.rect(self.subscreen1, (0,0,0), (j*56 + 382, i*40 + 50, 52, 7))

                name_text1.update("%s" %(characters[character_index]), pos=(0,126*2+36*4), color=[255,255,255],right=668)
                name_text1.draw(self.subscreen1)
                text_list[6].update("Change Persona", pos=(0,126*2+5*36+4), color=[255,255,255], right=668)
                text_list[6].draw(self.subscreen1)

                text_list[5].update("%s" %(persona_names[character_index][p_index_1]), pos=(380+66,5*36+80), color=[255,255,255])
                text_list[5].draw(self.subscreen1)

                self.arrow_pos += 0.5
                if self.arrow_pos >= 10:
                    self.arrow_pos = 0

                if self.arrow_pos <= 5:
                    a = int(self.arrow_pos)
                else:
                    a = 10-int(self.arrow_pos)

                if self.icon_alpha > 0:
                    self.icon_alpha -= 25 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    if self.icon_alpha < 0:
                        self.icon_alpha = 0

                self.subscreen1.blit(self.up_arrow, (660,126*2+36*4-8-a))
                self.subscreen1.blit(self.down_arrow, (660,126*2+36*4+18+a))
                self.subscreen1.blit(self.left_arrow, (660+18-a,126*2+36*5+8))
                self.subscreen1.blit(self.right_arrow, (660+30+a,126*2+36*5+8))

            elif self.mode == 8:
                self.subscreen1.blit(self.menu_back[1], (0,0))
                temp1 = self.rot_center(self.rotate_img[1], self.rotate_img[1].get_rect(), self.rotate_angle)[0]
                temp2 = self.rot_center(self.rotate_img[6], self.rotate_img[6].get_rect(), self.rotate_angle)[0]
                self.subscreen1.blit(temp1, temp1.get_rect(center=(60,-10)))
                self.subscreen1.blit(temp2, temp2.get_rect(center=(720-60,540)))

                if self.interface_index == 0:
                    if shake1 > 0:
                        shake1 /= int(2 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))
                else:
                    shake1 = 0
                    
                self.subscreen1.blit(self.silhouettes[story_index], self.silhouettes[story_index].get_rect(bottomleft=(-80-shake1,240*2+100)))
                self.subscreen1.blit(self.portraits[story_index], self.portraits[story_index].get_rect(bottomleft=(-80,240*2+100)))

                for i in range(10):
                    if story_strings[story_index][i] != text_list[i].text:
                        text_list[i].update(story_strings[story_index][i], pos=(320,i*24+12), color=colors[menu_index][1] if i == 0 else [255,255,255])

                pygame.draw.rect(self.subscreen1, [0,0,0], (320,58+12,368,4))

                for i in range(10):
                    text_list[i].draw(self.subscreen1)

                name_text1.update("%s" %(story_characters[story_index]), pos=(0,126*2+36*4), color=[255,255,255],right=668)
                name_text1.draw(self.subscreen1)

                if story_strings[story_index][0] != text_list[10].text:
                    text_list[10].update(story_strings[story_index][0], pos=(0,126*2+5*36+4), color=[255,255,255], right=668)
                text_list[10].draw(self.subscreen1)

                self.arrow_pos += 0.5
                if self.arrow_pos >= 10:
                    self.arrow_pos = 0

                if self.arrow_pos <= 5:
                    a = int(self.arrow_pos)
                else:
                    a = 10-int(self.arrow_pos)

                if self.icon_alpha > 0:
                    self.icon_alpha -= 25 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                    if self.icon_alpha < 0:
                        self.icon_alpha = 0

                self.subscreen1.blit(self.up_arrow, (660,126*2+36*4-8-a))
                self.subscreen1.blit(self.down_arrow, (660,126*2+36*4+18+a))

            elif self.mode == 4:
                self.subscreen1.blit(self.menu_back[3], (0,0))
                temp1 = self.rot_center(self.rotate_img[3], self.rotate_img[3].get_rect(), self.rotate_angle)[0]
                self.subscreen1.blit(temp1, temp1.get_rect(center=(60,-45)))
                temp2 = self.rot_center(self.rotate_img[8], self.rotate_img[8].get_rect(), self.rotate_angle)[0]
                self.subscreen1.blit(temp2, temp2.get_rect(center=(720-60,540)))

                if not rendered_awards:
                    name_text2.update("Finish 1st, 2nd, or 3rd with each P4 char.", (16*2,18*6*2), color=colors[6][0] if (self.achievements[2] and\
                                      self.achievements[3] and self.achievements[4] and self.achievements[5] and self.achievements[6] and\
                                      self.achievements[7] and self.achievements[8]) else colors[menu_index][1])
                    name_text3.update("Finish 1st, 2nd, or 3rd with each P3 char.", (16*2,18*5*2), color=colors[6][0] if (self.achievements[9] and\
                                      self.achievements[10] and self.achievements[11] and self.achievements[12] and self.achievements[13] and\
                                      self.achievements[14] and self.achievements[15] and self.achievements[16]) else colors[menu_index][1])
                    name_text4.update("Complete Free Race in under 1 min", (16*2,18*4*2), color=colors[6][0] if self.achievements[18] else colors[menu_index][1])
                    name_text5.update("Complete Story Mode for the first time", (16*2,18*3*2), color=colors[6][0] if self.achievements[29] else colors[menu_index][1])
                    name_text7.update("Complete Free Race with 100% HP", (16*2,18*7*2), color=colors[6][0] if self.achievements[0] else colors[menu_index][1])
                    name_text8.update("Complete Free Race with less than 10% HP", (16*2,18*8*2), color=colors[6][0] if self.achievements[20] else colors[menu_index][1])

                    rendered_awards = True
                name_text2.draw(self.subscreen1)
                name_text3.draw(self.subscreen1)
                name_text4.draw(self.subscreen1)
                name_text5.draw(self.subscreen1)
                name_text7.draw(self.subscreen1)
                name_text8.draw(self.subscreen1)

                text_list[6].update("Press any key to return to title.", pos=(10,36*6+230), color=[255,255,255])
                text_list[6].draw(self.subscreen1)

            elif self.mode == 5:
                self.subscreen1.blit(self.menu_back[4], (0,0))
                temp1 = self.rot_center(self.rotate_img[4], self.rotate_img[4].get_rect(), self.rotate_angle)[0]
                self.subscreen1.blit(temp1, temp1.get_rect(center=(60,-45)))
                temp2 = self.rot_center(self.rotate_img[9], self.rotate_img[9].get_rect(), self.rotate_angle)[0]
                self.subscreen1.blit(temp2, temp2.get_rect(center=(720-60,540)))

                if self.interface_index == 0:
                    if abs(title_shake) > 0:
                        title_shake /= -2
                else:
                    title_shake = 0
                    
                name_text1.update("Screen Size: %s" %screen_size[self.screen_index],
                                  center=(360+title_shake,18*2*2+title_shake) if option_index == 0 else (360,18*2*2),
                                  color=colors[6][0] if option_index == 0 else colors[menu_index][1])
                name_text2.update("Interface: %s" %interface[self.interface_index],
                                  center=(360+title_shake,18*3*2+title_shake) if option_index == 1 else (360,18*3*2),
                                  color=colors[6][0] if option_index == 1 else colors[menu_index][1])
                name_text3.update("BGM Toggle: %s" %music_toggle[self.music_index],
                                  center=(360+title_shake,18*4*2+title_shake) if option_index == 2 else (360,18*4*2),
                                  color=colors[6][0] if option_index == 2 else colors[menu_index][1])
                name_text4.update("Sound Toggle: %s" %sound_toggle[self.sound_index],
                                  center=(360+title_shake,18*5*2+title_shake) if option_index == 3 else (360,18*5*2),
                                  color=colors[6][0] if option_index == 3 else colors[menu_index][1])
                name_text5.update("Restrict Input: %s" %inputs[self.input_index],
                                  center=(360+title_shake,18*6*2+title_shake) if option_index == 4 else (360,18*6*2),
                                  color=colors[6][0] if option_index == 4 else colors[menu_index][1])
                name_text6.update("Engine Class: %s" %self.engine_string[self.engine_class],
                                  center=(360+title_shake,18*7*2+title_shake) if option_index == 5 else (360,18*7*2),
                                  color=colors[6][0] if option_index == 5 else colors[menu_index][1])
                name_text7.update("Reset to Defaults",
                                  center=(360+title_shake,18*8*2+title_shake) if option_index == 6 else (360,18*8*2),
                                  color=colors[6][0] if option_index == 6 else colors[menu_index][1])
                name_text8.update("Back",
                                  center=(360+title_shake,18*10*2+title_shake) if option_index == 7 else (360,18*10*2),
                                  color=colors[6][0] if option_index == 7 else colors[menu_index][1])
                name_text1.draw(self.subscreen1)
                name_text2.draw(self.subscreen1)
                name_text3.draw(self.subscreen1)
                name_text4.draw(self.subscreen1)
                name_text5.draw(self.subscreen1)
                name_text6.draw(self.subscreen1)
                name_text7.draw(self.subscreen1)
                name_text8.draw(self.subscreen1)

                text_list[6].update(option_strings[option_index], pos=(10,36*6+230), color=[255,255,255])
                text_list[6].draw(self.subscreen1)

            elif self.mode == 6:
                self.subscreen1.blit(self.menu_back[2], (0,0))
                temp1 = self.rot_center(self.rotate_img[2], self.rotate_img[2].get_rect(), self.rotate_angle)[0]
                self.subscreen1.blit(temp1, temp1.get_rect(center=(60,-45)))
                temp2 = self.rot_center(self.rotate_img[7], self.rotate_img[7].get_rect(), self.rotate_angle)[0]
                self.subscreen1.blit(temp2, temp2.get_rect(center=(720-60,540)))

                if self.interface_index == 0:
                    if abs(title_shake) > 0:
                        title_shake /= -2
                else:
                    title_shake = 0

                name_text1.update("Up", (16*12+title_shake,18*2*2+title_shake) if config_index == 0 else (16*12,18*2*2),
                                  color=colors[6][0] if config_index == 0 else colors[menu_index][1])
                name_text10.update("Setting..." if (setting and config_index ==  0) else ("None" if self.gamepad[0] == -1 else ("%s" %self.button_names[self.gamepad[0]] if self.gamepad[0] in [1001,1010,990,999] else "Button %d" %self.gamepad[0])),
                                   (16*12+270+title_shake,18*2*2+title_shake) if config_index == 0 else (16*12+270,18*2*2),
                                   color=colors[6][0] if config_index == 0 else colors[menu_index][1])

                name_text2.update("Down", (16*12+title_shake,18*3*2+title_shake) if config_index == 1 else (16*12,18*3*2),
                                  color=colors[6][0] if config_index == 1 else colors[menu_index][1])
                name_text11.update("Setting..." if (setting and config_index ==  1) else ("None" if self.gamepad[1] == -1 else ("%s" %self.button_names[self.gamepad[1]] if self.gamepad[1] in [1001,1010,990,999] else "Button %d" %self.gamepad[1])),
                                   (16*12+270+title_shake,18*3*2+title_shake) if config_index == 1 else (16*12+270,18*3*2),
                                   color=colors[6][0] if config_index == 1 else colors[menu_index][1])

                name_text3.update("Left", (16*12+title_shake,18*4*2+title_shake) if config_index == 2 else (16*12,18*4*2),
                                  color=colors[6][0] if config_index == 2 else colors[menu_index][1])
                name_text12.update("Setting..." if (setting and config_index == 2) else ("None" if self.gamepad[2] == -1 else ("%s" %self.button_names[self.gamepad[2]] if self.gamepad[2] in [1001,1010,990,999] else "Button %d" %self.gamepad[2])),
                                   (16*12+270+title_shake,18*4*2+title_shake) if config_index == 2 else (16*12+270,18*4*2),
                                   color=colors[6][0] if config_index == 2 else colors[menu_index][1])

                name_text4.update("Right", (16*12+title_shake,18*5*2+title_shake) if config_index == 3 else (16*12,18*5*2),
                                  color=colors[6][0] if config_index == 3 else colors[menu_index][1])
                name_text13.update("Setting..." if (setting and config_index == 3) else ("None" if self.gamepad[3] == -1 else ("%s" %self.button_names[self.gamepad[3]] if self.gamepad[3] in [1001,1010,990,999] else "Button %d" %self.gamepad[3])),
                                   (16*12+title_shake+270,18*5*2+title_shake) if config_index == 3 else (16*12+270,18*5*2),
                                   color=colors[6][0] if config_index == 3 else colors[menu_index][1])

                name_text5.update("Accel / Confirm", (16*12+title_shake,18*6*2+title_shake) if config_index == 4 else (16*12,18*6*2),
                                  color=colors[6][0] if config_index == 4 else colors[menu_index][1])
                name_text14.update("Setting..." if (setting and config_index == 4) else ("None" if self.gamepad[4] == -1 else ("%s" %self.button_names[self.gamepad[4]] if self.gamepad[4] in [1001,1010,990,999] else "Button %d" %self.gamepad[4])),
                                   (16*12+title_shake+270,18*6*2+title_shake+title_shake) if config_index == 4 else (16*12+270,18*6*2),
                                   color=colors[6][0] if config_index == 4 else colors[menu_index][1])

                name_text6.update("Skill / Cancel", (16*12+title_shake,18*7*2+title_shake) if config_index == 5 else (16*12,18*7*2),
                                  color=colors[6][0] if config_index == 5 else colors[menu_index][1])
                name_text15.update("Setting..." if (setting and config_index == 5) else ("None" if self.gamepad[5] == -1 else ("%s" %self.button_names[self.gamepad[5]] if self.gamepad[5] in [1001,1010,990,999] else "Button %d" %self.gamepad[5])),
                                   (16*12+title_shake+270,18*7*2+title_shake) if config_index == 5 else (16*12+270,18*7*2),
                                   color=colors[6][0] if config_index == 5 else colors[menu_index][1])

                name_text7.update("Pause", (16*12+title_shake,18*8*2+title_shake) if config_index == 6 else (16*12,18*8*2),
                                  color=colors[6][0] if config_index == 6 else colors[menu_index][1])
                name_text16.update("Setting..." if (setting and config_index == 6) else ("None" if self.gamepad[6] == -1 else ("%s" %self.button_names[self.gamepad[6]] if self.gamepad[6] in [1001,1010,990,999] else "Button %d" %self.gamepad[6])),
                                   (16*12+title_shake+270,18*8*2+title_shake) if config_index == 6 else (16*12+270,18*8*2),
                                   color=colors[6][0] if config_index == 6 else colors[menu_index][1])

                name_text8.update("Clear All", (16*12+title_shake,18*9*2+title_shake) if config_index == 7 else (16*12,18*9*2),
                                  color=colors[6][0] if config_index == 7 else colors[menu_index][1])
                name_text9.update("Back", (16*12+title_shake,18*10*2+title_shake) if config_index == 8 else (16*12,18*10*2),
                                  color=colors[6][0] if config_index == 8 else colors[menu_index][1])
                name_text1.draw(self.subscreen1)
                name_text2.draw(self.subscreen1)
                name_text3.draw(self.subscreen1)
                name_text4.draw(self.subscreen1)
                name_text5.draw(self.subscreen1)
                name_text6.draw(self.subscreen1)
                name_text7.draw(self.subscreen1)
                name_text8.draw(self.subscreen1)
                name_text9.draw(self.subscreen1)
                name_text10.draw(self.subscreen1)
                name_text11.draw(self.subscreen1)
                name_text12.draw(self.subscreen1)
                name_text13.draw(self.subscreen1)
                name_text14.draw(self.subscreen1)
                name_text15.draw(self.subscreen1)
                name_text16.draw(self.subscreen1)

                text_list[6].update("Set button inputs.", pos=(10,36*6+230), color=[255,255,255])
                text_list[6].draw(self.subscreen1)

            elif self.mode == 7:

                if self.interface_index == 0:
                    if abs(title_shake) > 0:
                        title_shake /= -2
                else:
                    title_shake = 0

                for q in range(13):
                    if q == new_course:
                        name_text1.update(self.stage_names[q], (title_shake,28*q+30+title_shake), color=[255,255,255], right=710)
                        name_text1.draw(self.subscreen1)
                    else:
                        if q > new_course:
                            text_list[q].update(self.stage_names[q], (0,28*q+36), color=colors[6][1], right=710)
                        else:
                            text_list[q].update(self.stage_names[q], (0,28*q+36), color=colors[6][1], right=710)
                        text_list[q].draw(self.subscreen1)

                #name_text1.update("%s" %(self.stage_names[new_course]), pos=(0,126*2+36*4+36), color=[255,255,255],right=660)
                #name_text1.draw(self.subscreen1)

                text_list[6].update("Choose a track.", pos=(10,36*6+230), color=[255,255,255])
                text_list[6].draw(self.subscreen1)

            if old_screen_index == 1:
                 pygame.transform.smoothscale(self.subscreen1,self.full_res,self.screen)
            else:
                self.screen.blit(self.subscreen1, (0,0))

            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self._quit()

                elif e.type == pygame.JOYHATMOTION:
                    if self.sound_index == 0 and e.value != (0,0):
                        self.select_sound.play()
                    if self.mode == 1:
                        if e.value[0]*10 + e.value[1] + 1000 == self.gamepad[0]:
                            menu_index -= 1
                            if menu_index == -1:
                                menu_index = 5
                            title_shake = 8

                        elif e.value[0]*10 + e.value[1] + 1000 == self.gamepad[1]:
                            menu_index += 1
                            if menu_index == 6:
                                menu_index = 0
                            title_shake = 8

                    elif self.mode == 2:
                        if e.value[0]*10 + e.value[1] + 1000 == self.gamepad[0]:
                            p_index_1 = 0
                            shake1 = 96
                            character_index -= 1
                            if character_index == -1:
                                character_index = len(characters)-1
                            while characters[character_index] == None:
                                character_index -= 1
                                if character_index == -1:
                                    character_index = len(characters)-1

                        elif e.value[0]*10 + e.value[1] + 1000 == self.gamepad[1]:
                            p_index_1 = 0
                            shake1 = 96
                            character_index += 1
                            if character_index == len(characters):
                                character_index = 0
                            while characters[character_index] == None:
                                character_index += 1
                                if character_index == len(characters):
                                    character_index = 0

                        elif e.value[0]*10 + e.value[1] + 1000 == self.gamepad[2]:
                            self.icon_alpha = 255
                            p_index_1 -= 1
                            if p_index_1 == -1:
                                p_index_1 = 6

                        elif e.value[0]*10 + e.value[1] + 1000 == self.gamepad[3]:
                            self.icon_alpha = 255
                            p_index_1 += 1
                            if p_index_1 == 7:
                                p_index_1 = 0

                    elif self.mode == 8:
                        if e.value[0]*10 + e.value[1] + 1000 == self.gamepad[0]:
                            p_index_1 = 0
                            old_story_index = story_index
                            story_index -= 1
                            if story_index == -1:
                                story_index = len(story_characters)-1
                            while story_characters[story_index] == None:
                                story_index -= 1
                                if story_index == -1:
                                    story_index = len(story_characters)-1
                            if old_story_index != story_index:
                                shake1 = 96

                        elif e.value[0]*10 + e.value[1] + 1000 == self.gamepad[1]:
                            p_index_1 = 0
                            old_story_index = story_index
                            story_index += 1
                            if story_index == len(story_characters):
                                story_index = 0
                            while story_characters[story_index] == None:
                                story_index += 1
                                if story_index == len(story_characters):
                                    story_index = 0
                            if old_story_index != story_index:
                                shake1 = 96

                    elif self.mode == 5:
                        if e.value[0]*10 + e.value[1] + 1000 == self.gamepad[0]:
                            title_shake = 16
                            option_index -= 1
                            if option_index == -1:
                                option_index = 7
                        elif e.value[0]*10 + e.value[1] + 1000 == self.gamepad[1]:
                            title_shake = 16
                            option_index += 1
                            if option_index == 8:
                                option_index = 0

                    elif self.mode == 6:
                        if setting:
                            if e.value == (0,1):
                                self.gamepad[config_index] = 1001
                            elif e.value == (0,-1):
                                self.gamepad[config_index] = 999
                            elif e.value == (-1,0):
                                self.gamepad[config_index] = 990
                            elif e.value == (1,0):
                                self.gamepad[config_index] = 1010
                            setting = False
                        else:
                            if e.value[0]*10 + e.value[1] + 1000 == self.gamepad[0]:
                                title_shake = 16
                                config_index -= 1
                                if config_index == -1:
                                    config_index = 8
                            elif e.value[0]*10 + e.value[1] + 1000 == self.gamepad[1]:
                                title_shake = 16
                                config_index += 1
                                if config_index == 9:
                                    config_index = 0

                    elif self.mode == 7:
                        if e.value[0]*10 + e.value[1] + 1000 == self.gamepad[0]:
                            new_course -= 1
                            if new_course == -1:
                                new_course = len(self.stage_names)-1
                            title_shake = 16
                        elif e.value[0]*10 + e.value[1] + 1000 == self.gamepad[1]:
                            new_course += 1
                            if new_course == len(self.stage_names):
                                new_course = 0
                            title_shake = 16
                        if new_course != old_course:
                            self.reset_main(new_course, is_title=True)
                            old_course = new_course

                elif e.type == pygame.JOYBUTTONDOWN:
                    if self.mode == 6:
                        if setting and config_index <= 6:
                            if self.sound_index == 0:
                                self.confirm_sound.play()
                            self.gamepad[config_index] = e.button
                            setting = False
                        else:
                            if e.button == self.gamepad[5]:
                                if self.sound_index == 0:
                                    self.confirm_sound.play()
                                self.reset_main(11, is_title=True)
                                self.mode = 1
                            elif e.button == self.gamepad[0]:
                                if self.sound_index == 0:
                                    self.select_sound.play()
                                title_shake = 16
                                config_index -= 1
                                if config_index == -1:
                                    config_index = 8
                            elif e.button == self.gamepad[1]:
                                if self.sound_index == 0:
                                    self.select_sound.play()
                                title_shake = 16
                                config_index += 1
                                if config_index == 9:
                                    config_index = 0
                            elif e.button == self.gamepad[4]:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                if config_index <= 6:
                                    setting = True if not setting else False
                                elif config_index == 7:
                                    self.gamepad = [-1,-1,-1,-1,-1,-1,-1]
                                elif config_index == 8:
                                    self.reset_main(11, is_title=True)
                                    self.mode = 1
                    else:
                        if e.button == self.gamepad[0]:
                            if self.sound_index == 0:
                                self.select_sound.play()
                                
                            if self.mode == 1:
                                menu_index -= 1
                                if menu_index == -1:
                                    menu_index = 5
                                title_shake = 16
                                
                            elif self.mode == 2:
                                p_index_1 = 0
                                shake1 = 96
                                character_index -= 1
                                if character_index == -1:
                                    character_index = len(characters) - 1
                                while characters[character_index] == None:
                                    character_index -= 1
                                    if character_index == -1:
                                        character_index = len(characters) - 1

                            elif self.mode == 8:
                                p_index_1 = 0
                                old_story_index = story_index
                                story_index -= 1
                                if story_index == -1:
                                    story_index = len(story_characters) - 1
                                while story_characters[story_index] == None:
                                    story_index -= 1
                                    if story_index == -1:
                                        story_index = len(story_characters) - 1
                                if old_story_index != story_index:
                                    shake1 = 96

                            elif self.mode == 5:
                                title_shake = 16
                                option_index -= 1
                                if option_index == -1:
                                    option_index = 7
                            elif self.mode == 7:
                                new_course -= 1
                                if new_course == -1:
                                    new_course = len(self.stage_names)-1
                                if new_course != old_course:
                                    self.reset_main(new_course, is_title=True)
                                    old_course = new_course
                                title_shake = 16

                        elif e.button == self.gamepad[1]:
                            if self.sound_index == 0:
                                self.select_sound.play()
                                
                            if self.mode == 1:
                                menu_index += 1
                                if menu_index == 6:
                                    menu_index = 0
                                title_shake = 16

                            elif self.mode == 2:
                                p_index_1 = 0
                                shake1 = 96
                                character_index += 1
                                if character_index == len(characters):
                                    character_index = 0
                                while characters[character_index] == None:
                                    character_index += 1
                                    if character_index == len(characters):
                                        character_index = 0

                            elif self.mode == 8:
                                p_index_1 = 0
                                old_story_index = story_index
                                story_index += 1
                                if story_index == len(story_characters):
                                    story_index = 0
                                while story_characters[story_index] == None:
                                    story_index += 1
                                    if story_index == len(story_characters):
                                        story_index = 0
                                if old_story_index != story_index:
                                    shake1 = 96

                            elif self.mode == 5:
                                title_shake = 16
                                option_index += 1
                                if option_index == 8:
                                    option_index = 0
                            elif self.mode == 7:
                                new_course += 1
                                if new_course == len(self.stage_names):
                                    new_course = 0
                                if new_course != old_course:
                                    self.reset_main(new_course, is_title=True)
                                    old_course = new_course
                                title_shake = 16

                        elif e.button == self.gamepad[2]:
                            if self.mode == 2:
                                if self.sound_index == 0:
                                    self.select_sound.play()
                                self.icon_alpha = 255
                                p_index_1 -= 1
                                if p_index_1 == -1:
                                    p_index_1 = 6

                        elif e.button == self.gamepad[3]:
                            if self.mode == 2:
                                if self.sound_index == 0:
                                    self.select_sound.play()
                                self.icon_alpha = 255
                                p_index_1 += 1
                                if p_index_1 == 7:
                                    p_index_1 = 0

                        elif e.button == self.gamepad[4]:
                            if self.mode == 1:
                                if self.sound_index == 0:
                                    self.confirm_sound.play()
                                if menu_index == 0:
                                    self.mode = 2
                                elif menu_index == 1:
                                    self.mode = 8
                                elif menu_index == 2:
                                    self.mode = 6
                                elif menu_index == 3:
                                    self.mode = 4
                                elif menu_index == 4:
                                    self.mode = 5
                                elif menu_index == 5:
                                    self._quit()
                            elif self.mode == 2:
                                if self.sound_index == 0:
                                    self.confirm_sound.play()
                                self.reset_main(new_course, is_title=True)
                                self.mode = 7
                            elif self.mode == 8:
                                if self.sound_index == 0:
                                    self.confirm_sound.play()
                                self.reset_main(new_course, is_title=True)
                                self.stage_intro(story_strings[story_index][0])
                                run_story = self.run_story(story_index)
                                story_mode = True
                            elif self.mode == 4:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                self.reset_main(11, is_title=True)
                                self.mode = 1
                            elif self.mode == 5:
                                if option_index == 0:
                                    if self.sound_index == 0:
                                        self.menu_sound.play()
                                    self.screen_index += 1
                                    if self.screen_index == 2:
                                        self.screen_index = 0
                                elif option_index == 1:
                                    if self.sound_index == 0:
                                        self.menu_sound.play()
                                    self.interface_index += 1
                                    if self.interface_index == 2:
                                        self.interface_index = 0
                                elif option_index == 2:
                                    if self.sound_index == 0:
                                        self.menu_sound.play()
                                    if self.is_audio_enabled:
                                        self.music_index += 1
                                        if self.music_index == 2:
                                            self.music_index = 0
                                    if self.music_index == 0:
                                        pygame.mixer.music.stop()
                                        pygame.mixer.music.load("res/sound/bgm01.ogg")
                                        pygame.mixer.music.set_volume(0.8)
                                        pygame.mixer.music.play(-1)
                                    else:
                                        pygame.mixer.music.stop()
                                elif option_index == 3:
                                    if self.sound_index == 0:
                                        self.menu_sound.play()
                                    if self.is_audio_enabled:
                                        self.sound_index += 1
                                        if self.sound_index == 2:
                                            self.sound_index = 0
                                elif option_index == 4:
                                    if self.sound_index == 0:
                                        self.menu_sound.play()
                                    self.input_index += 1
                                    if self.input_index == 3:
                                        self.input_index = 0
                                elif option_index == 5:
                                    if self.sound_index == 0:
                                        self.menu_sound.play()
                                    self.engine_class -= 1
                                    if self.engine_class == -1:
                                        self.engine_class = 2
                                elif option_index == 6:
                                    if self.sound_index == 0:
                                        self.menu_sound.play()
                                    self.screen_index = 0
                                    self.interface_index = 0
                                    if self.is_audio_enabled:
                                        self.music_index = 0
                                        self.sound_index = 0
                                    else:
                                        self.music_index = 1
                                        self.sound_index = 1
                                    self.input_index = 0
                                    self.engine_class = 1
                                    if self.music_index == 0:
                                        pygame.mixer.music.stop()
                                        pygame.mixer.music.load("res/sound/bgm01.ogg")
                                        pygame.mixer.music.set_volume(0.8)
                                        pygame.mixer.music.play(-1)
                                    else:
                                        pygame.mixer.music.stop()
                                elif option_index == 7:
                                    if self.sound_index == 0:
                                        self.confirm_sound.play()
                                    if old_screen_index != self.screen_index:
                                        old_screen_index = self.screen_index
                                        if self.screen_index == 0:
                                            self.screen = pygame.display.set_mode((720,480))
                                        else:
                                            if self.is_hw:
                                                self.screen = pygame.display.set_mode(self.full_res, FULLSCREEN)
                                            else:
                                                self.screen = pygame.display.set_mode(self.full_res, FULLSCREEN)
                                    self.reset_main(11, is_title=True)
                                    self.mode = 1
                            elif self.mode == 7:
                                if self.sound_index == 0:
                                    self.confirm_sound.play()
                                running = True

                        elif e.button == self.gamepad[5]:
                            if self.mode in [2,3,4,8]:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                self.reset_main(11, is_title=True)
                                self.mode = 1
                            elif self.mode == 5:
                                if self.sound_index == 0:
                                    self.confirm_sound.play()
                                if old_screen_index != self.screen_index:
                                    old_screen_index = self.screen_index
                                    if self.screen_index == 0:
                                        self.screen = pygame.display.set_mode((720,480))
                                    else:
                                        self.screen = pygame.display.set_mode(self.full_res, FULLSCREEN)
                                self.reset_main(11, is_title=True)
                                self.mode = 1
                            elif self.mode == 7:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                self.mode = 2


                elif e.type == pygame.KEYDOWN:
                    if self.mode == 1:
                        if e.key == pygame.K_ESCAPE:
                            self._quit()
                        elif e.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_z]:
                            if self.sound_index == 0:
                                self.confirm_sound.play()
                            if menu_index == 0:
                                self.mode = 2
                            elif menu_index == 1:
                                self.mode = 8
                            elif menu_index == 2:
                                self.mode = 6
                            elif menu_index == 3:
                                self.mode = 4
                            elif menu_index == 4:
                                self.mode = 5
                            elif menu_index == 5:
                                self._quit()
                        elif e.key in [pygame.K_UP, pygame.K_w]:
                            if self.sound_index == 0:
                                self.select_sound.play()
                            menu_index -= 1
                            if menu_index == -1:
                                menu_index = 5
                            title_shake = 16

                        elif e.key in [pygame.K_DOWN, pygame.K_s]:
                            if self.sound_index == 0:
                                self.select_sound.play()
                            menu_index += 1
                            if menu_index == 6:
                                menu_index = 0
                            title_shake = 16

                    elif self.mode in [2,8]:
                        if e.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                            if self.sound_index == 0:
                                self.menu_sound.play()
                            self.reset_main(11, is_title=True)
                            self.mode = 1
                        elif e.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_z]:
                            if self.sound_index == 0:
                                self.confirm_sound.play()
                            self.reset_main(new_course, is_title=True)
                            if self.mode == 2:
                                self.mode = 7
                            else:
                                self.stage_intro(story_strings[story_index][0])
                                run_story = self.run_story(story_index)
                                story_mode = True
                                
                        elif e.key == pygame.K_UP:
                            if self.mode == 2:
                                p_index_1 = 0
                                shake1 = 96
                                if self.sound_index == 0:
                                    self.select_sound.play()
                                character_index -= 1
                                if character_index == -1:
                                    character_index = len(characters) - 1
                                while characters[character_index] == None:
                                    character_index -= 1
                                    if character_index == -1:
                                        character_index = len(characters)-1

                            elif self.mode == 8:
                                p_index_1 = 0
                                old_story_index = story_index
                                if self.sound_index == 0:
                                    self.select_sound.play()
                                story_index -= 1
                                if story_index == -1:
                                    story_index = len(story_characters) - 1
                                while story_characters[story_index] == None:
                                    story_index -= 1
                                    if story_index == -1:
                                        story_index = len(story_characters)-1
                                if old_story_index != story_index:
                                    shake1 = 96

                        elif e.key == pygame.K_DOWN:
                            if self.mode == 2:
                                p_index_1 = 0
                                shake1 = 96
                                if self.sound_index == 0:
                                    self.select_sound.play()
                                character_index += 1
                                if character_index == len(characters):
                                    character_index = 0
                                while characters[character_index] == None:
                                    character_index += 1
                                    if character_index == len(characters):
                                        character_index = 0
                            elif self.mode == 8:
                                p_index_1 = 0
                                old_story_index = story_index
                                if self.sound_index == 0:
                                    self.select_sound.play()
                                story_index += 1
                                if story_index == len(story_characters):
                                    story_index = 0
                                while story_characters[story_index] == None:
                                    story_index += 1
                                    if story_index == len(story_characters):
                                        story_index = 0
                                if old_story_index != story_index:
                                    shake1 = 96

                        elif e.key == pygame.K_LEFT and self.mode == 2:
                            if self.sound_index == 0:
                                self.select_sound.play()
                            self.icon_alpha = 255
                            p_index_1 -= 1
                            if p_index_1 == -1:
                                p_index_1 = 6

                        elif e.key == pygame.K_RIGHT and self.mode == 2:
                            if self.sound_index == 0:
                                self.select_sound.play()
                            self.icon_alpha = 255
                            p_index_1 += 1
                            if p_index_1 == 7:
                                p_index_1 = 0


                    elif self.mode == 4:
                        if self.sound_index == 0:
                            self.menu_sound.play()
                        self.reset_main(11, is_title=True)
                        self.mode = 1
                    elif self.mode == 5:
                        if e.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                            if self.sound_index == 0:
                                self.confirm_sound.play()
                            if old_screen_index != self.screen_index:
                                old_screen_index = self.screen_index
                                if self.screen_index == 0:
                                    self.screen = pygame.display.set_mode((720,480))
                                else:
                                    self.screen = pygame.display.set_mode(self.full_res, FULLSCREEN)
                            self.reset_main(11, is_title=True)
                            self.mode = 1
                        elif e.key in [pygame.K_UP, pygame.K_w]:
                            title_shake = 16
                            if self.sound_index == 0:
                                self.select_sound.play()
                            option_index -= 1
                            if option_index == -1:
                                option_index = 7
                        elif e.key in [pygame.K_DOWN, pygame.K_s]:
                            title_shake = 16
                            if self.sound_index == 0:
                                self.select_sound.play()
                            option_index += 1
                            if option_index == 8:
                                option_index = 0
                        elif e.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_z]:
                            if option_index == 0:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                self.screen_index += 1
                                if self.screen_index == 2:
                                    self.screen_index = 0
                            elif option_index == 1:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                self.interface_index += 1
                                if self.interface_index == 2:
                                    self.interface_index = 0
                            elif option_index == 2:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                if self.is_audio_enabled:
                                    self.music_index += 1
                                    if self.music_index == 2:
                                        self.music_index = 0
                                if self.music_index == 0:
                                    pygame.mixer.music.stop()
                                    pygame.mixer.music.load("res/sound/bgm01.ogg")
                                    pygame.mixer.music.set_volume(0.8)
                                    pygame.mixer.music.play(-1)
                                else:
                                    pygame.mixer.music.stop()
                            elif option_index == 3:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                if self.is_audio_enabled:
                                    self.sound_index += 1
                                    if self.sound_index == 2:
                                        self.sound_index = 0
                            elif option_index == 4:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                self.input_index += 1
                                if self.input_index == 3:
                                    self.input_index = 0
                            elif option_index == 5:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                self.engine_class -= 1
                                if self.engine_class == -1:
                                    self.engine_class = 2
                            elif option_index == 6:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                self.screen_index = 0
                                self.interface_index = 0
                                if self.is_audio_enabled:
                                    self.music_index = 0
                                    self.sound_index = 0
                                else:
                                    self.music_index = 1
                                    self.sound_index = 1
                                self.input_index = 0
                                self.engine_class = 1
                                if self.music_index == 0:
                                    pygame.mixer.music.stop()
                                    pygame.mixer.music.load("res/sound/bgm01.ogg")
                                    pygame.mixer.music.set_volume(0.8)
                                    pygame.mixer.music.play(-1)
                                else:
                                    pygame.mixer.music.stop()
                            elif option_index == 7:
                                if self.sound_index == 0:
                                    self.confirm_sound.play()
                                if old_screen_index != self.screen_index:
                                    old_screen_index = self.screen_index
                                    if self.screen_index == 0:
                                        self.screen = pygame.display.set_mode((720,480))
                                    else:
                                        self.screen = pygame.display.set_mode(self.full_res, FULLSCREEN)
                                self.reset_main(11, is_title=True)
                                self.mode = 1

                    elif self.mode == 6:
                        if e.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                            if self.sound_index == 0:
                                self.menu_sound.play()
                            if setting:
                                setting = False
                            else:
                                self.reset_main(11, is_title=True)
                                self.mode = 1
                        elif e.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_z]:
                            if config_index <= 6:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                setting = True if not setting else False
                            elif config_index == 7:
                                if self.sound_index == 0:
                                    self.menu_sound.play()
                                self.gamepad = [-1,-1,-1,-1,-1,-1,-1]
                            else:
                                if self.sound_index == 0:
                                    self.confirm_sound.play()
                                self.reset_main(11, is_title=True)
                                self.mode = 1
                        elif e.key in [pygame.K_UP, pygame.K_w] and not setting:
                            title_shake = 16
                            if self.sound_index == 0:
                                self.select_sound.play()
                            config_index -= 1
                            if config_index == -1:
                                config_index = 8
                        elif e.key in [pygame.K_DOWN, pygame.K_s] and not setting:
                            title_shake = 16
                            if self.sound_index == 0:
                                self.select_sound.play()
                            config_index += 1
                            if config_index == 9:
                                config_index = 0
                    elif self.mode == 7:
                        if e.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                            if self.sound_index == 0:
                                self.menu_sound.play()
                            self.mode = 2
                        elif e.key in [pygame.K_UP, pygame.K_w]:
                            if self.sound_index == 0:
                                self.select_sound.play()
                            new_course -= 1
                            if new_course == -1:
                                new_course = len(self.stage_names)-1
                            if new_course != old_course:
                                self.reset_main(new_course, is_title=True)
                                old_course = new_course
                            title_shake = 16
                        elif e.key in [pygame.K_DOWN, pygame.K_s]:
                            if self.sound_index == 0:
                                self.select_sound.play()
                            new_course += 1
                            if new_course == len(self.stage_names):
                                new_course = 0
                            if new_course != old_course:
                                self.reset_main(new_course, is_title=True)
                                old_course = new_course
                            title_shake = 16
                        elif e.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_z]:
                            if self.sound_index == 0:
                                self.confirm_sound.play()
                            running = True

        if running:
            self.main(new_course, None, character_index, persona_list[character_index][p_index_1]-1)
        elif story_mode:
            self.main(run_story[0], run_story[1], story_index, persona_list[story_index][p_index_1]-1)
        return

    def reset_main(self, course, is_title=False):
        if not is_title and self.music_index == 0:
            pygame.mixer.music.load("res/sound/course%02d.ogg" %(course+1))
            pygame.mixer.music.set_volume(0.5)

        self.reset(self.players, is_title, course)

        ## Initialize loop variables
        dt = 0

        self.countdown = 0.0
        self.music_playing = False
        self.pause_text_1 = Text("", (0,0))
        self.pause_text_2 = Text("", (0,0))
        self.pause_text_3 = Text("", (0,0))
        self.item_text = Text("", (0,0), size=24)
        self.health_text = Text("", (0,0), size=24, border=True)
        self.win_text = []
        for i in range(8):
            temp_text = Text("", (135*2,36*(i+2)) if i != 6 else (135*2, 36*5), border=True)
            self.win_text.append(temp_text)

    def stage_intro(self, string):
        text1 = Text("", (0,0))
        if self.music_index == 0:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("res/sound/bgm02.ogg")
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)

        while True:
            self.subscreen1.fill((0,0,0))
            self.clock.tick(self.fps)

            self.stage_alpha -= 10 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
            self.stage_mask.set_alpha(max(0,int(self.stage_alpha)))

            text1.update(string, center=(180*2,18*6*2))
            text1.draw(self.subscreen1)
            self.subscreen1.blit(self.stage_mask, (0,0))
            pygame.display.flip()

            if self.screen_index == 0:
                self.screen.blit(self.subscreen1, (0,0))
            else:
               pygame.transform.smoothscale(self.subscreen1,self.full_res,self.screen)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self._quit()
                elif e.type == pygame.KEYDOWN:
                    if self.stage_alpha <= -260:
                        self.stage_alpha = 255
                        return True
                elif e.type == pygame.JOYBUTTONDOWN and self.stage_alpha <= -260:
                    self.stage_alpha = 255
                    return True

    def run_credits(self):
        f = open("res/script/8.dat", "r").readlines()
        credit_text = []
        for i in range(len(f)):
            credit_text.append(Text(f[i].replace("\n",""), size=24, pos=(32,480+26*i)))

        if self.music_index == 0:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("res/sound/bgm15.ogg")
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)

        while True:
            self.subscreen1.fill((0,0,0))

            self.stage_alpha -= 1 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
            self.stage_mask.set_alpha(max(0,int(self.stage_alpha)))

            self.credits_01.set_alpha(255-int(self.credit_alpha))
            self.subscreen1.blit(self.credits_01, (0,0))

            self.credits_02.set_alpha(int(self.credit_alpha))
            self.subscreen1.blit(self.credits_02, (0,0))
            self.credit_alpha = min(255, self.credit_alpha + 0.1)

            self.subscreen1.blit(self.stage_mask, (0,0))

            self.clock.tick(self.fps)

            for i in range(len(credit_text)):
                if credit_text[i].y > -40 and credit_text[-1].y > 240:
                    credit_text[i].update(pos=(32,credit_text[i].y-int(max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))))

            for i in range(len(credit_text)):
                credit_text[i].draw(self.subscreen1)

            if self.screen_index == 0:
                self.screen.blit(self.subscreen1, (0,0))
            else:
                pygame.transform.smoothscale(self.subscreen1,self.full_res,self.screen)

            pygame.display.flip()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self._quit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.stage_alpha = 255
                        return
                elif e.type == pygame.JOYBUTTONDOWN:
                    if e.button == self.gamepad[6]:
                        self.stage_alpha = 255
                        return

    def run_story(self, index):
        story_text1 = Text("", (90,340), color=[0,0,0], size=24)
        story_text2 = Text("", (108,380), size=20)
        story_text3 = Text("", (108,380+20), size=20)
        story_text4 = Text("", (108,380+40), size=20)
        story_text5 = Text("Confirm: Advance Dialogue", (4,2), size=20)
        story_text6 = Text("ESC / Pause: Skip Scene", (4,2), size=20)
        
        f = open("res/script/%d.dat" %(index+1), "r").readlines()
        self.scenes = []
        count = 0
        racers = []
        for p in range(len(f)):
            if f[p].startswith("RACE = "):
                split = f[p].strip("RACE = ").split(",")
                for item in split:
                    racers.append(int(item))
            elif f[p].startswith("SCENE: "):
                bgm = None
                pos = 0
                background = 0
                char1 = self.scenes[count-1].char1 if count > 0 else None
                char2 = self.scenes[count-1].char2 if count > 0 else None
                lines = []
                split = f[p].strip("SCENE: ").split(", ")
                for item in split:
                    if item.startswith("LEFT = "):
                        char1 = int(item.strip("LEFT = "))
                        pos = -1
                    elif item.startswith("RIGHT = "):
                        char2 = int(item.strip("RIGHT = "))
                        pos = 1
                    elif item.startswith("BGM = "):
                        bgm = int(item.strip("BGM = "))
                    elif item.startswith("SCENE = "):
                        background = int(item.strip("SCENE = "))
                for i in range(1,5):
                    lines.append(f[p+i].replace("\n",""))

                temp = self.Scene(pos, char1, char2, bgm, background, lines)
                self.scenes.append(temp)
                count += 1

        self.players = []
        index1 = random.randint(0,6)
        self.players.append(Player(index1,"TITLE", 1, is_title=True))

        course = self.scenes[0].background
        self.reset_main(course, is_title=True)

        old_scene = -1
        current_scene = 0
        current_bgm = None
        shake1 = 32
        num1 = 0
        num2 = 0
        num3 = 0

        while True:
            self.subscreen1.fill((0,0,0))
            rate = self.clock.tick(self.fps)

            self.players[0].inputs[0] = False
            self.players[0].inputs[1] = False

            segment = self.find_segment(self.players[0].position)

            if (segment.curve < 0 and self.players[0].player_x > self.players[0].lane) or\
               self.players[0].player_x > 1:
                self.players[0].inputs[0] = True
            elif (segment.curve > 0 and self.players[0].player_x < self.players[0].lane) or\
                 self.players[0].player_x < -1:
                self.players[0].inputs[1] = True

            self.players[0].inputs[2] = True
            self.players[0].speed = self.max_speed * 0.15

            dt = 1.0/rate
            self.update(self.step, is_title=True)

            if shake1 > 0:
                shake1 /= int(2 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))

            self.render(False, course, is_title=True)
            if old_scene != current_scene:
                if self.sound_index == 0:
                    self.text_scroll.play(-1)
                old_scene = current_scene

            if self.scenes[current_scene].bgm != current_bgm and self.scenes[current_scene].bgm != None and self.music_index == 0:
                current_bgm = self.scenes[current_scene].bgm
                pygame.mixer.music.stop()
                if current_bgm != 0:
                    pygame.mixer.music.load("res/sound/bgm%02d.ogg" %(self.scenes[current_scene].bgm))
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)

            if self.scenes[current_scene].char1 != None:
                if current_scene == 0 or self.scenes[current_scene].char1 != self.scenes[current_scene-1].char1:
                    self.subscreen1.blit(self.portraits[self.scenes[current_scene].char1-1],
                                         self.portraits[self.scenes[current_scene].char1-1].get_rect(bottomleft=(-80+shake1,240*2+100)))
                else:
                    self.subscreen1.blit(self.portraits[self.scenes[current_scene].char1-1],
                                         self.portraits[self.scenes[current_scene].char1-1].get_rect(bottomleft=(-80,240*2+100-(shake1 if self.scenes[current_scene].pos == -1 else 0))))
            if self.scenes[current_scene].char2 != None:
                if current_scene == 0 or self.scenes[current_scene].char2 != self.scenes[current_scene-1].char2:
                    self.subscreen1.blit(self.portraits[self.scenes[current_scene].char2-1],
                                         self.portraits[self.scenes[current_scene].char2-1].get_rect(bottomright=(800+shake1,240*2+100)))
                else:
                    self.subscreen1.blit(self.portraits[self.scenes[current_scene].char2-1],
                                         self.portraits[self.scenes[current_scene].char2-1].get_rect(bottomright=(800,240*2+100-(shake1 if self.scenes[current_scene].pos == 1 else 0))))
            self.subscreen1.blit(self.text_box, (0,0))

            pygame.draw.rect(self.subscreen1, (0,0,0), (0,0,720,30))
            story_text5.draw(self.subscreen1)
            story_text6.update(right=716)
            story_text6.draw(self.subscreen1)

            story_text1.update(self.scenes[current_scene].lines[0])
            story_text2.update(self.scenes[current_scene].lines[1])
            story_text3.update(self.scenes[current_scene].lines[2])
            story_text4.update(self.scenes[current_scene].lines[3])
            story_text1.draw(self.subscreen1)
            story_text2.draw_sub(self.subscreen1, num1)
            story_text3.draw_sub(self.subscreen1, num2)
            story_text4.draw_sub(self.subscreen1, num3)

            num1 += int(10 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))
            if num1 >= story_text2.width:
                num1 = story_text2.width
                num2 += int(10 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))
            if num2 >= story_text3.width:
                num2 = story_text3.width
                num3 += int(10 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0))
            if num3 >= story_text4.width:
                num3 = story_text4.width
                if self.sound_index == 0:
                    self.text_scroll.stop()

            self.arrow_pos += 1
            if self.arrow_pos >= 10:
                self.arrow_pos = 0

            if self.arrow_pos <= 5:
                a = int(self.arrow_pos)
            else:
                a = 10-int(self.arrow_pos)

            if num1 == story_text2.width and num2 == story_text3.width and num3 == story_text4.width:
                if num3 > 6:
                    self.subscreen1.blit(pygame.transform.scale(self.down_arrow, (32,16)),(story_text4.width+105,425+a))
                elif num2 > 6:
                    self.subscreen1.blit(pygame.transform.scale(self.down_arrow, (32,16)),(story_text3.width+105,405+a))
                elif num1 > 6:
                    self.subscreen1.blit(pygame.transform.scale(self.down_arrow, (32,16)),(story_text2.width+105,385+a))

            if self.screen_index == 0:
                self.screen.blit(self.subscreen1, (0,0))
            else:
               pygame.transform.smoothscale(self.subscreen1,self.full_res,self.screen)

            pygame.display.flip()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self._quit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        if self.sound_index == 0:
                            self.text_scroll.stop()
                        return course, racers
                    else:
                        if num1 < story_text2.width or num2 < story_text3.width or num3 < story_text4.width:
                            num1 = story_text2.width
                            num2 = story_text3.width
                            num3 = story_text4.width
                        else:
                            current_scene += 1
                            shake1 = 32
                            num1 = 0
                            num2 = 0
                            num3 = 0
                            if current_scene >= len(self.scenes):
                                return course, racers
                elif e.type == pygame.JOYBUTTONDOWN:
                    if e.button == self.gamepad[6]:
                        if self.sound_index == 0:
                            self.text_scroll.stop()
                        return course, racers
                    else:
                        if num1 < story_text2.width or num2 < story_text3.width or num3 < story_text4.width:
                            num1 = story_text2.width
                            num2 = story_text3.width
                            num3 = story_text4.width
                        else:
                            current_scene += 1
                            shake1 = 32
                            num1 = 0
                            num2 = 0
                            num3 = 0
                            if current_scene >= len(self.scenes):
                                return course, racers

    def display_unlock(self):
        text1 = Text("", (0,0))
        if self.music_index == 0:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("res/sound/bgm04.ogg")
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)


        if self.unlocked[0] or self.unlocked[1] or self.unlocked[2] or self.unlocked[3] or self.unlocked[4]\
           or self.unlocked[5] or self.unlocked[6] or self.unlocked[7] or self.unlocked[8] or self.unlocked[9]:
            if self.unlocked[0]:
                text1.update("Unlocked Gold Teddie in Free Race!", center=(180*2,18*6*2))
            elif self.unlocked[1]:
                text1.update("Unlocked Rise in Free Race!", center=(180*2,18*6*2))
            elif self.unlocked[2]:
                text1.update("Unlocked Yosuke in Story Mode!", center=(180*2,18*6*2))
            elif self.unlocked[3]:
                text1.update("Unlocked Yukiko in Story Mode!", center=(180*2,18*6*2))
            elif self.unlocked[4]:
                text1.update("Unlocked Chie in Story Mode!", center=(180*2,18*6*2))
            elif self.unlocked[5]:
                text1.update("Unlocked Kanji in Story Mode!", center=(180*2,18*6*2))
            elif self.unlocked[6]:
                text1.update("Unlocked Naoto in Story Mode!", center=(180*2,18*6*2))
            elif self.unlocked[7]:
                text1.update("Unlocked Teddie in Story Mode!", center=(180*2,18*6*2))
            elif self.unlocked[8]:
                text1.update("Unlocked P3 cast in Free Race!", center=(180*2,18*6*2))

            self.unlocked = (False, False, False, False, False,
                             False, False, False, False, False)

            while True:
                self.subscreen1.fill((0,0,0))
                self.clock.tick(self.fps)

                self.stage_alpha -= 15 * max(1.0, 1.0 + (60 - self.clock.get_fps()) / 60.0)
                if self.stage_alpha < 255:
                    self.stage_mask.set_alpha(max(0,int(self.stage_alpha)))
                else:
                    self.stage_mask.set_alpha(min(255,int(1024-self.stage_alpha)))
                if self.stage_alpha >= 1024:
                    return

                text1.draw(self.subscreen1)
                self.subscreen1.blit(self.stage_mask, (0,0))
                pygame.display.flip()

                if self.screen_index == 0:
                    self.screen.blit(self.subscreen1, (0,0))
                else:
                    pygame.transform.smoothscale(self.subscreen1,self.full_res,self.screen)

                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        self._quit()
                    elif e.type == pygame.KEYDOWN:
                        self.stage_alpha = 255
                        return
                    elif e.type == pygame.JOYBUTTONDOWN:
                        self.stage_alpha = 255
                        return

    def main(self, course, racers, index1, p_index_1):
        if self.music_index == 0:
            pygame.mixer.music.stop()

        ## Initialize player objects
        self.players = []
        if racers != None:
            players = racers
        else:
            players = [i for i in range(0,16)]

        positions = []
        start_pos = -1.0
        for i in range(min(6,len(players))):
            positions.append(start_pos)
            start_pos += 2/5.0

        random.shuffle(positions)
        random.shuffle(players)

        self.players.append(Player(index1, "P1", p_index_1, is_title=False, player_x=positions[0], position=0, engine=self.engine_class))
        count = 1
        for p in players:
            if p != index1 and count < len(positions):
                idno = "CPU"
                player = Player(p, idno, 0, is_title=False, player_x=positions[count], position=0, engine=self.engine_class)
                self.players.append(player)
                count += 1


        if not self.stage_intro(self.stage_names[course]):
            return

        self.reset_main(course)
        finish = False

        while True:
            rate = self.clock.tick(self.fps)
            dt = 1.0/rate
            finish = self.update(self.step)
            if (self.countdown/1000)%60 > 3:
                if self.get_inputs(dt, finish):
                    if self.mode == 8 and self.players[0].laps == self.max_laps and self.players[0].num == 6 and self.players[0].place == 1:
                        self.run_credits()
                    self.display_unlock()
                    return
                if not self.pause:
                    self.time += rate
                    if not self.music_playing and self.music_index == 0:
                        pygame.mixer.music.play(-1)
                        self.music_playing = True
                    self.get_cpu_inputs(dt)
                    self.update_places()
            else:
                self.countdown += rate
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        self._quit()

            self.render(finish, course)

if __name__ == "__main__":
    main = Main()
    while True:
        main.splash()
