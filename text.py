import pygame
from pygame.locals import *

## Text wrapper to handle TTF fonts ##
######################################
class Text(object):
    def __init__(self, string, pos, color=[255,255,255], size=32, num=1, border=False, outline=[0,0,0]):
        self.font = pygame.font.Font("res/font/font%d.ttf" %num, size)
        self.x = pos[0]        ## X topleft
        self.y = pos[1]        ## Y topleft
        self.color = color     ## Color tuple
        self.outline = outline ## Default outline
        self.text = string     ## Text string to draw
        self.height = self.font.get_height() ## Height of font
        #self.border = border
        self.black_text = self.font.render(self.text, True, self.outline)
        self.white_text = self.font.render(self.text, True, self.color)
        self.width = self.white_text.get_width()
        self.is_border = border

    def draw(self, surface):
        # Draw the black outline first, "border" pixels wide
        if self.is_border:
            for i in range(-2,3):
                for j in range(-2,3):
                    surface.blit(self.black_text, (self.x+i, self.y+j))
        ## Draw the white text next at the same position
        surface.blit(self.white_text, (self.x, self.y))

    def draw_sub(self, surface, width):
        ## Draw the white text next at the same position
        if width < self.width:
            surface.blit(self.white_text.subsurface((0,0,width,self.height)), (self.x, self.y))
        else:
            surface.blit(self.white_text.subsurface((0,0,self.width,self.height)), (self.x, self.y))

    def update(self, string=None, pos=None, center=None, color=None, right=None, size=None, antialiased=True):
        ## Update various parameters as needed
        changed = False
        if color != None and self.color != color: ## Update the color
            self.color = color
            changed = True
        if string != None and string != self.text:
            self.text = string
            changed = True
        if changed:
            if self.is_border:
                self.black_text = self.font.render(self.text, antialiased, self.outline)
            self.white_text = self.font.render(self.text, antialiased, self.color)
            self.width = self.white_text.get_width()
        if pos != None:        ## Update the topleft
            self.x = pos[0]
            self.y = pos[1]
        if center != None:     ## Update the center
            self.x = center[0] - self.font.size(self.text)[0]/2
            self.y = center[1]
        if right != None:      ## Update the rightmost point
            self.x = right - self.font.size(self.text)[0]
