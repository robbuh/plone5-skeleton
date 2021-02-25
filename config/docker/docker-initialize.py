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
    #             https://github.com/plone/plone.docker/blob/master/5.2/5.2.2/python37/docker-initialize.py

    def buildout(self):
        """ Buildout from environment variables
        """
        # Already configured
        if os.path.exists(self.custom_conf):
            return

        findlinks = self.env.get("FIND_LINKS", "").strip().split()

        eggs = self.env.get("PLONE_ADDONS",
               self.env.get("ADDONS", "")).strip().split()

        zcml = self.env.get("PLONE_ZCML",
               self.env.get("ZCML", "")).strip().split()

        develop = self.env.get("PLONE_DEVELOP",
                  self.env.get("DEVELOP", "")).strip().split()

        site = self.env.get("PLONE_SITE",
               self.env.get("SITE", "")).strip()

        profiles = self.env.get("PLONE_PROFILES",
                   self.env.get("PROFILES", "")).strip().split()

        versions = self.env.get("PLONE_VERSIONS",
                   self.env.get("VERSIONS", "")).strip().split()

        sources = self.env.get("SOURCES", "").strip()
        sources = sources and [x.strip() for x in sources.split(",")]

        #relstorage = self.relstorage_conf()
        relstorage = ""

        buildout_extends = ((develop or sources)
                            and "develop.cfg" or "buildout.cfg")

        # If profiles not provided. Install ADDONS :default profiles
        if not profiles:
            for egg in eggs:
                base = egg.split("=")[0]
                profiles.append("%s:default" % base)

        enabled = bool(site)
        if not (eggs or zcml or relstorage or develop or enabled):
            return

        buildout = BUILDOUT_TEMPLATE.format(
            buildout_extends=buildout_extends,
            findlinks="\n\t".join(findlinks),
            eggs="\n\t".join(eggs),
            zcml="\n\t".join(zcml),
            relstorage=relstorage,
            develop="\n\t".join(develop),
            profiles="\n\t".join(profiles),
            versions="\n".join(versions),
            sources="\n".join(sources),
            site=site or "Plone",
            enabled=enabled,
        )

        # If we need to create a plonesite and we have a zeo setup
        # configure collective.recipe.plonesite properly
        server = self.env.get("ZEO_ADDRESS", None)
        if server:
            buildout += ZEO_INSTANCE_TEMPLATE.format(
                zeoaddress=server,
            )

        with open(self.custom_conf, 'w') as cfile:
            cfile.write(buildout)

    def setup(self):
        """ Configure
        """
        super(Environment, self).setup()

        self.buildout()

    __call__ = setup

BUILDOUT_TEMPLATE = """
[buildout]
extends = {buildout_extends}
find-links += {findlinks}
develop += {develop}
eggs += {eggs}
zcml += {zcml}

[instance]
rel-storage =
  {relstorage}

[plonesite]
enabled = {enabled}
site-id = {site}
profiles += {profiles}

[versions]
{versions}

[sources]
{sources}
"""

def initialize():
    """ Configure
    """
    environment = Environment()
    environment.setup()

if __name__ == "__main__":
    initialize()
