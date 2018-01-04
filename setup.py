from distutils.core import setup
import py2exe, os, glob

dfiles = []

rootdir = 'C:/Users/Joey Schamoley/Documents/GitHub/racing-all-afternoon/'

def get_files(dfiles, directory):
    d1 = rootdir + directory
    for files in os.listdir(d1):
        f1 = d1 + files
        if os.path.isfile(f1):
            f2 = directory, [f1]
            dfiles.append(f2)
        else:
            get_files(dfiles, directory + files + '/')

get_files(dfiles, 'res/')

setup(
    version = "1.0",
    description = "Persona 4: Racing All Afternoon",
    name = "Persona 4: Racing All Afternoon",
    url = "",
    author = "MaxieManDanceParty",
    author_email = "",
    license = "MIT License",

    # targets to build
    windows = [{
        'script': "main.py",
        'icon_resources': [(0, 'res/img/favicon.ico')],
        'copyright': ""
    }],
    options = {'py2exe': {
        'optimize': 2,
        'bundle_files': 1,
        'compressed': True,
        'excludes': [],
        'packages': [],
        'dll_excludes': [''],
        'includes': [
        'const',
        'course',
        'main',
        'player',
        'text',
        'render',
        ],
        'excludes':[
            'setup',
            ],
        'dist_dir': 'outputs'}
               },
    zipfile = None,
    data_files = [
        ('res/font', glob.glob('res/font/*.ttf')),
        ('res/data', glob.glob('res/data/*.dat')),
        ('res/stage', glob.glob('res/stage/*.dat')),
        ('res/char', glob.glob('res/char/*.dat')),
        ('res/img', glob.glob('res/img/*.png') + glob.glob('res/img/*.ico')),
        ('res/persona', glob.glob('res/persona/*.dat')),
        ('res/script', glob.glob('res/script/*.dat')),
        ('res/sound', glob.glob('res/sound/*.ogg')),
        ('res/sound/1', glob.glob('res/sound/1/*.ogg')),
        ('res/sound/2', glob.glob('res/sound/2/*.ogg')),
        ('res/sound/3', glob.glob('res/sound/3/*.ogg')),
        ('res/sound/4', glob.glob('res/sound/4/*.ogg')),
        ('res/sound/5', glob.glob('res/sound/5/*.ogg')),
        ('res/sound/6', glob.glob('res/sound/6/*.ogg')),
        ('res/sound/7', glob.glob('res/sound/7/*.ogg')),
        ('res/sound/8', glob.glob('res/sound/8/*.ogg')),
        ('res/sound/9', glob.glob('res/sound/9/*.ogg')),
        ('res/sound/10', glob.glob('res/sound/10/*.ogg')),
        ('res/sound/11', glob.glob('res/sound/11/*.ogg')),
        ('res/sound/12', glob.glob('res/sound/12/*.ogg')),
        ('res/sound/13', glob.glob('res/sound/13/*.ogg')),
        ('res/sound/14', glob.glob('res/sound/14/*.ogg')),
        ('res/sound/15', glob.glob('res/sound/15/*.ogg')),
        ('res/sound/16', glob.glob('res/sound/16/*.ogg')),
        ('res/sound/17', glob.glob('res/sound/17/*.ogg')),
        ],
    )
