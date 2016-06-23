import os

import arkInit
arkInit.init()

import tryout
tryout.runFolder(os.path.realpath(__file__), callback=None, bail=True)
