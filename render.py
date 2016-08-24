import pygame, random
from pygame.locals import *
from const import *

## Global functions for 3D polygonal rendering ##
#################################################

## Calculate the horizontal distance at which to place the wall
def render_wall_width(projected_road_width):
    return projected_road_width / 0.45

## Calculate the horizontal distance to place the rumble strip
def render_rumble_width(projected_road_width, lanes):
    return projected_road_width / 2

## Calculate the width of a lane marker
def render_lane_marker_width(projected_road_width, lanes):
    return projected_road_width / max(10, 4*lanes)

## Draw a polygon with four points to the screen, filled with the color
def render_polygon(screen, x1, y1, x2, y2, x3, y3, x4, y4, color):
    pygame.draw.polygon(screen,color, [[x1,y1],[x2,y2],[x3,y3],[x4,y4]])

## Render the left and right walls, as well as the ceiling
def render_wall(screen, width, lanes, x1, y1, w1, x2, y2, w2, n, draw_dist, color, dark_color):
    ## Get x distance to place wall
    r1 = render_wall_width(w1)
    r2 = render_wall_width(w2)

    ## Calculate color fade with fog; color[2] = wall, color[4] = fog
    rate1 = (float(color[2][0]-color[4][0]),
             float(color[2][1]-color[4][1]),
             float(color[2][2]-color[4][2]))
    ## Wall color is [a,b,c]
    a = int(color[2][0] - n*rate1[0]/draw_dist)
    b = int(color[2][1] - n*rate1[1]/draw_dist)
    c = int(color[2][2] - n*rate1[2]/draw_dist)

    ## Draw them
    render_polygon(screen, x1-w1-r1, y1, x2-w2-r2, y2, x2-w2-r2, y2-r2-20, x1-w1-r1, y1-r1-20, [a,b,c])
    render_polygon(screen, x1+w1+r1, y1, x2+w2+r2, y2, x2+w2+r2, y2-r2-20, x1+w1+r1, y1-r1-20, [a,b,c])

## Render the road and offroad on the ground
def render_segment(screen, width, lanes, x1, y1, w1, x2, y2, w2, color):
    ## Calculate widths
    r1 = render_rumble_width(w1, lanes)
    r2 = render_rumble_width(w2, lanes)
    l1 = render_lane_marker_width(w1, lanes)
    l2 = render_lane_marker_width(w2, lanes)

    ## Draw a large rect for the base, then draw trapezoids for the road proper
    ## color[0] = road, color[1] = offroad, color[3] = rumble
    pygame.draw.rect(screen, color[1], (0, y2, width, y1-y2))
    render_polygon(screen, x1-w1-r1, y1, x1-w1, y1, x2-w2, y2, x2-w2-r2, y2, color[3])
    render_polygon(screen, x1+w1+r1, y1, x1+w1, y1, x2+w2, y2, x2+w2+r2, y2, color[3])
    render_polygon(screen, x1-w1, y1, x1+w1, y1, x2+w2, y2, x2-w2, y2, color[0])

    ## If we're on an odd alternation, draw a dashed lane marker
    if color[5] != None:
        lanew1 = w1*2/lanes
        lanew2 = w2*2/lanes
        lanex1 = x1 - w1 + lanew1
        lanex2 = x2 - w2 + lanew2
        for LANE in range(1, lanes):
            render_polygon(screen, lanex1-l1/2, y1, lanex1+l1/2, y1, lanex2+l2/2, y2, lanex2-l2/2, y2, color[5])
            lanex1 += lanew1
            lanex2 += lanew2

## Render a sprite on-screen, i.e. item or character
def render_sprite(screen, width, height, resolution, road_width, sprite, scale, dest_x, dest_y, offset_x,
           offset_y, clip_y, is_player=False, item=None, lightning=None, is_item=False,
           shadow=None, floor=None, smoke=None, boost=0.0, threshold=1.0, attack=0.0):

    ## Scale down the destination dimensions
    dest_w = (sprite.get_width() * scale * width / 2) * 0.3 * (1/40.0) * road_width
    dest_h = (sprite.get_height() * scale * width / 2) * 0.3 * (1/40.0) * road_width

    ## Item parameter: Whether or not an item icon appears above the sprite's head
    if item != None:
        dest_w_1 = (item.get_width() * scale * width / 2) * 0.3 * (1/40.0) * road_width
        dest_h_1 = (item.get_height() * scale * width / 2) * 0.3 * (1/40.0) * road_width

    ## Lightning parameter: Whether or not lightning is striking the sprite
    if lightning != None:
        dest_w_2 = (lightning.get_width() * scale * width / 2) * 0.3 * (1/40.0) * road_width
        dest_h_2 = (lightning.get_height() * scale * width / 2) * 0.3 * (1/40.0) * road_width

    ## Shadow parameter: Whether or not a shadow is present beneath the sprite
    if shadow != None:
        dest_w_3 = (shadow.get_width() * scale * width / 2) * 0.3 * (1/40.0) * road_width
        dest_h_3 = (shadow.get_height() * scale * width / 2) * 0.3 * (1/40.0) * road_width

    ## If not a player or item, don't offset the x coordinate
    dest_x += 0 if not (is_player or is_item) else dest_w * offset_x
    ## If it's not a player, normalize the y height
    if not is_player:
        dest_y += dest_h * (offset_y or 0)

    ## Check for clipping on horizon, then proceed if we're not clipping
    clip_h = max(0, dest_y+dest_h-clip_y) if clip_y else 0
    dest_w = int(dest_w)

    if clip_h < dest_h:
        ## Make sure the sprite isn't so huge
        if dest_h < 260 and dest_w < 260:

            if not is_player:
                dest_h = int(dest_h-clip_h)
            else:
                dest_h = int(dest_h)

            ## Draw the shadow
            if shadow != None and floor != None:
                temp = pygame.transform.scale(shadow,(int(dest_w_3),int(dest_h_3)))
                screen.blit(temp, (dest_x, floor))

            ## Draw the sprite
            screen.blit(pygame.transform.scale(sprite,(dest_w,dest_h)), (dest_x, dest_y))

            ## Render the exhaust as circles growing and shrinking randomly
            if smoke != None:
                pos1 = (int(dest_x+dest_w/4),int(dest_y+dest_h))
                pos2 = (int(dest_x+dest_w*7/8.0),int(dest_y+dest_h))

                ## Calculate random circle sizes, larger if mini-turbo is active
                smoke1 = int((random.randint(1 if boost <= threshold-0.5 else (8 if boost <= threshold else 10),smoke[0] + (0 if boost <= threshold-0.5 else (8 if boost <= threshold else 10))) * scale * width / 2) * 0.3 * (1/40.0) * road_width)
                smoke2 = int((random.randint(1 if boost <= threshold-0.5 else (8 if boost <= threshold else 10),smoke[0] + (0 if boost <= threshold-0.5 else (8 if boost <= threshold else 10))) * scale * width / 2) * 0.3 * (1/40.0) * road_width)
                smoke3 = int((random.randint(1 if boost <= threshold-0.5 else (8 if boost <= threshold else 10),smoke[0] + (0 if boost <= threshold-0.5 else (8 if boost <= threshold else 10))) * scale * width / 2) * 0.3 * (1/40.0) * road_width)

                a = random.randint(3 if 0 < boost <= threshold-0.5 else 5, 12 if 0 < boost <= threshold-0.5 else 17)
                b = random.randint(3 if 0 < boost <= threshold-0.5 else 5, 12 if 0 < boost <= threshold-0.5 else 17)
                c = random.randint(3 if 0 < boost <= threshold-0.5 else 5, 12 if 0 < boost <= threshold-0.5 else 17)
                d = random.randint(3 if 0 < boost <= threshold-0.5 else 5, 12 if 0 < boost <= threshold-0.5 else 17)

                ## Flicker the color
                tempcolor = random.choice((COLORS.BOOST1,COLORS.BOOST2))

                ## Draw the exhaust
                if smoke1 > 0:
                    pygame.draw.circle(screen, COLORS.BLACK_SMOKE if boost < 0 else (COLORS.SMOKE if boost < threshold-0.5 else (COLORS.BOOST1 if boost < threshold else tempcolor)), pos1, smoke1)
                    pygame.draw.circle(screen, COLORS.BLACK_SMOKE if boost < 0 else (COLORS.SMOKE if boost < threshold-0.5 else (COLORS.BOOST1 if boost < threshold else tempcolor)), pos2, smoke1)
                if smoke2 > 0:
                    pygame.draw.circle(screen, COLORS.BLACK_SMOKE if boost < 0 else (COLORS.SMOKE if boost < threshold-0.5 else (COLORS.BOOST1 if boost < threshold else tempcolor)), [pos1[0]-int(a*scale*width/2* 0.3 * (1/40.0) * road_width),pos1[1]], smoke2)
                    pygame.draw.circle(screen, COLORS.BLACK_SMOKE if boost < 0 else (COLORS.SMOKE if boost < threshold-0.5 else (COLORS.BOOST1 if boost < threshold else tempcolor)), [pos2[0]-int(b*scale*width/2* 0.3 * (1/40.0) * road_width),pos2[1]], smoke2)
                if smoke3 > 0:
                    pygame.draw.circle(screen, COLORS.BLACK_SMOKE if boost < 0 else (COLORS.SMOKE if boost < threshold-0.5 else (COLORS.BOOST1 if boost < threshold else tempcolor)), [pos1[0]+int(c*scale*width/2* 0.3 * (1/40.0) * road_width),pos1[1]], smoke3)
                    pygame.draw.circle(screen, COLORS.BLACK_SMOKE if boost < 0 else (COLORS.SMOKE if boost < threshold-0.5 else (COLORS.BOOST1 if boost < threshold else tempcolor)), [pos2[0]-int(d*scale*width/2* 0.3 * (1/40.0) * road_width),pos2[1]], smoke3)

            ## If performing a physical attack, render the attack radius
            if attack > 0:
                radius = (100 - attack) * scale * width / 2 * 0.3 * (1/40.0) * road_width
                pos = (int(dest_x+dest_w/2),int(dest_y+dest_h/2))
                pygame.draw.circle(screen, [230,230,230], pos, max(3,int(radius)), 3)

            ## If an item is above the character, blit it
            if item != None:
                temp_1 = pygame.transform.scale(item,(int(dest_w_1/2),int(dest_h_1/2)))
                screen.blit(temp_1, temp_1.get_rect(topleft=(dest_x, dest_y-dest_h)))
            ## If lightning is above the character, blit it
            if lightning != None:
                new_dest_y = dest_y + dest_y * 0.1 * scale * width / 2 * 0.3 * (1/40.0) * road_width
                new_dest_x = dest_x + dest_x * 0.1 * scale * width / 2 * 0.3 * (1/40.0) * road_width
                temp_2 = pygame.transform.scale(lightning,(int(dest_w_2),int(dest_h_2)))
                screen.blit(temp_2, temp_2.get_rect(midbottom=(int(new_dest_x), int(new_dest_y))))

## Render a player unit; note that this supplies data to be fed into the above function, does not draw on its own
def render_cpu(screen, player, width, height, resolution, road_width, speed_percent, scale,
        dest_x, dest_y, steer, item, lightning, shadow, floor):

    ## Bounce due to motor
    bounce = (1.5 * random.random() * speed_percent * resolution) * random.choice((-1,1))

    ## Shaking occurs if you're frozen and you're mashing the D-Pad or other
    if player.shake:
        shake = 3.0 * random.random() * random.choice((-1,1))
    else:
        shake = 0

    ## Change the sprite to frozen if hit by bufu
    if player.frozen > 0:
        if player.no_control > 0:
            ## Illusion of spinning out
            temp = round(player.no_control * 10)
            if temp%3 == 0:
                player.sprite = player.player_left_frozen
            elif temp%3 == 1:
                player.sprite = player.player_straight_frozen
            elif temp%3 == 2:
                player.sprite = player.player_right_frozen
        else:
            ## Draw normally
            if steer < 0:
                player.sprite = player.player_left_frozen
            elif steer > 0:
                player.sprite = player.player_right_frozen
            else:
                player.sprite = player.player_straight_frozen
        smoke = None
    else: ## Default sprites
        if player.no_control > 0:
            ## Illusion of spinning out
            temp = round(player.no_control * 10)
            if temp%3 == 0:
                player.sprite = player.player_left
                smoke = [max(6,int(12 * bounce)), -1]
            elif temp%3 == 1:
                player.sprite = player.player_straight
                smoke = [max(6,int(12 * bounce)), 0]
            elif temp%3 == 2:
                player.sprite = player.player_right
                smoke = [max(6,int(12 * bounce)), 1]
        else:
            ## Draw normally
            if steer < 0:
                player.sprite = player.player_left
                smoke = [max(6,int(12 * bounce)), -1]
            elif steer > 0:
                player.sprite = player.player_right
                smoke = [max(6,int(12 * bounce)), 1]
            else:
                player.sprite = player.player_straight
                smoke = [max(6,int(12 * bounce)), 0]

    ## Data for extra things like exhaust and attacking radius
    temp_smoke = smoke if (player.player_y == 0 and player.speed > 0) else None
    temp_threshold = player.threshold
    temp_attack = player.attack

    ## Actually draw it
    render_sprite(screen, width, height, resolution, road_width, player.sprite, scale, dest_x + shake,
                dest_y + bounce + shake, -0.5, -1, 0, True, item, lightning, False, shadow,
                floor, temp_smoke, player.boost, temp_threshold, temp_attack)
