import random

## Course texture colors ##
###########################
class Course(object):
    def __init__(self, num):
        ## Default colors, fall back to these
        fog = [0,0,0]
        light_road = [0,0,0]
        dark_road = [0,0,0]
        light_offroad = [0,0,0]
        dark_offroad = [0,0,0]
        light_wall = [0,0,0]
        dark_wall = [0,0,0]
        light_rumble = [0,0,0]
        dark_rumble = [0,0,0]

        ## Course road geometry
        self.geometry = [0,0,0,0,0,0,0,0]
        last_seg = 0
        ## Start with a straightaway by default
        ## Exactly six "segments" are made
        for i in range(7):
            ## Add a segment that's different from the previous one
            self.geometry[i] = last_seg
            last_seg += random.choice((-1,1))
            if last_seg < 1:
                last_seg = 3
            elif last_seg > 3:
                last_seg = 1

        ## Length of each segment, larger number = longer strip
        self.strip = 3 ## Wall
        self.road = 2  ## Road

        ## Load texture colors to overwrite defaults
        f = open("res/stage/%d.dat" %num, "r").readlines()
        for line in f:
            if line.startswith("fog = "): ## Fog color to fade into
                temp = line.strip("fog = ").split(",")
                fog = [int(temp[0]),int(temp[1]),int(temp[2])]
            elif line.startswith("light_road = "): ## Light ground strip
                temp = line.strip("light_road = ").split(",")
                light_road = [int(temp[0]),int(temp[1]),int(temp[2])]
            elif line.startswith("dark_road = "): ## Dark ground strip
                temp = line.strip("dark_road = ").split(",")
                dark_road = [int(temp[0]),int(temp[1]),int(temp[2])]
            elif line.startswith("light_offroad = "): ## Light offroad strip
                temp = line.strip("light_offroad = ").split(",")
                light_offroad = [int(temp[0]),int(temp[1]),int(temp[2])]
            elif line.startswith("dark_offroad = "): ## Dark offroad strip
                temp = line.strip("dark_offroad = ").split(",")
                dark_offroad = [int(temp[0]),int(temp[1]),int(temp[2])]
            elif line.startswith("light_wall = "): ## Light wall strip
                temp = line.strip("light_wall = ").split(",")
                light_wall = [int(temp[0]),int(temp[1]),int(temp[2])]
            elif line.startswith("dark_wall = "): ## Dark wall strip
                temp = line.strip("dark_wall = ").split(",")
                dark_wall = [int(temp[0]),int(temp[1]),int(temp[2])]
            elif line.startswith("light_rumble = "): ## Light rumble strip
                temp = line.strip("light_rumble = ").split(",")
                light_rumble = [int(temp[0]),int(temp[1]),int(temp[2])]
            elif line.startswith("dark_rumble = "): ## Dark rumble strip
                temp = line.strip("dark_rumble = ").split(",")
                dark_rumble = [int(temp[0]),int(temp[1]),int(temp[2])]
            elif line.startswith("ceiling = "): ## Ceiling
                temp = line.strip("ceiling = ").split(",")
                ceiling = [int(temp[0]),int(temp[1]),int(temp[2])]
            elif line.startswith("strip = "): ## Length of wall segment
                self.strip = int(line.strip("strip = "))
            elif line.startswith("road = "): ## Length of road segment
                self.road = int(line.strip("road = "))

        ## Define start line, finish line, and dark and light strip lists
        white = [200,200,200]
        self.start = [white,white,light_wall, white, fog, white]
        self.finish = [white, white, dark_wall, white, fog, white]
        self.dark_colors = [dark_road, dark_offroad, dark_wall, dark_rumble, fog, None, ceiling]
        self.light_colors = [light_road, light_offroad, light_wall, light_rumble, fog, white, ceiling]
