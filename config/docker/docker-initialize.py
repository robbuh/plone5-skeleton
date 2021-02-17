#!/usr/bin/env python

import os
from contextlib import closing
import urllib.request, urllib.error, urllib.parse
from plone_initialize import Environment as PloneEnvironment
from shutil import copy


class Environment(PloneEnvironment):
    """ Configure container via environment variables
    """
    def __init__(self, **kwargs):
        super(Environment, self).__init__(**kwargs)

    # Put here your custom ENV vars
    # References: https://github.com/eea/eea.docker.plone/blob/master/src/docker/docker-initialize.py

def initialize():
    """ Configure
    """
    environment = Environment()
    environment.setup()

if __name__ == "__main__":
    initialize()
