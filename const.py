## Road structure containing defined constants ##
#################################################
class ROAD:
    class LENGTH:
        NONE = 0
        SHORT = 20
        MEDIUM = 40
        LONG = 60

    class HILL:
        NONE = 0
        LOW = 50
        MEDIUM = 90
        HIGH = 130

    class CURVE:
        NONE = 0
        EASY = 12
        MEDIUM = 16
        HARD = 24

## Colors structure containing constant color tuples ##
######################################################
class COLORS:
    SMOKE = [200,200,200]    ## Default smoke
    BLACK_SMOKE = [47,47,47] ## Burnout smoke
    BOOST1 = [128,128,255]   ## Turbo flash 1
    BOOST2 = [164,164,255]   ## Turbo flash 2
