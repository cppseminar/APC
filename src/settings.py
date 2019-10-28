"""This module will be for handling all setting in some nice way.  It should be
able to parse arguments, and later config files.  Basically you will just ask
this module for any setting you like"""


SETTINGS = None

class Settings:
    def __init__(self):
        self.verbose = False

SETTINGS = Settings()
