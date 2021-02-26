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

        self.threads = self.env.get('ZOPE_THREADS', '')
        self.fast_listen = self.env.get('ZOPE_FAST_LISTEN', '')
        self.force_connection_close = self.env.get('ZOPE_FORCE_CONNECTION_CLOSE', '')

        self.postgres_host = self.env.get("RELSTORAGE_HOST", None)
        self.postgres_user = self.env.get("RELSTORAGE_USER", None)
        self.postgres_password = self.env.get("RELSTORAGE_PASS", None)

        self.keep_history = False
        if self.env.get('RELSTORAGE_KEEP_HISTORY', 'false').lower() in ('true', 'yes', 'y', '1'):
            self.keep_history = True

        mode = self.env.get('ZOPE_MODE', 'standalone')
        conf = 'zope.conf'
        if mode == 'zeo':
            conf = 'zeo.conf'
        conf = '/plone/instance/parts/%s/etc/%s' % (mode, conf)
        if not os.path.exists(conf):
            mode = 'standalone'
            conf = '/plone/instance/parts/%s/etc/%s' % (mode, conf)

        self.mode = mode
        self.zope_conf = conf
        self.cors_conf = "/plone/instance/parts/%s/etc/package-includes/999-additional-overrides.zcml" % mode

        self.graylog = self.env.get('GRAYLOG', '')
        self.facility = self.env.get('GRAYLOG_FACILITY', self.mode)

        self.sentry = self.env.get('SENTRY_DSN', '')
        self._environment = self.env.get('ENVIRONMENT',
                            self.env.get('SENTRY_ENVIRONMENT', ''))

        self._conf = ''

        # Custom Buildout section
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

        buildout_extends = ((develop or sources)
                            and "develop.cfg" or "buildout.cfg")

        # If profiles not provided. Install ADDONS :default profiles
        if not profiles:
            for egg in eggs:
                base = egg.split("=")[0]
                profiles.append("%s:default" % base)

        enabled = bool(site)
        if not (eggs or zcml or develop or enabled):
            return

        buildout = BUILDOUT_TEMPLATE.format(
            buildout_extends=buildout_extends,
            findlinks="\n\t".join(findlinks),
            eggs="\n\t".join(eggs),
            zcml="\n\t".join(zcml),
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

        # End - Custom Buildout section

    @property
    def environment(self):
        """ Try to get environment from rancher-metadata
        """
        if not self._environment:
            url = "http://rancher-metadata/latest/self/stack/environment_name"
            try:
                with closing(urllib.request.urlopen(url)) as conn:
                    self._environment = conn.read()
            except Exception as err:
                self.log("Couldn't get environment from rancher-metadata: %s.", err)
                self._environment = "devel"
        return self._environment

    @property
    def conf(self):
        """ Zope conf
        """
        if not self._conf:
            with open(self.zope_conf, 'r') as zfile:
                self._conf = zfile.read()
        return self._conf

    @conf.setter
    def conf(self, value):
        """ Zope conf
        """
        self._conf = value

    def log(self, msg='', *args):
        """ Log message to console
        """
        print((msg % args))

    def zope_mode(self):
        """ Zope mode
        """
        self.log("Using bin/%s", self.mode)
        copy('/plone/instance/bin/%s' % self.mode, '/plone/instance/bin/instance')

    def setup_graylog(self):
        """ Send logs to graylog
        """
        if not self.graylog:
            return

        self.log("Sending logs to graylog: '%s' as facilty: '%s'", self.graylog, self.facility)

    def setup_sentry(self):
        """ Send tracebacks to sentry
        """
        if not self.sentry:
            return

        self.log("Sending errors to sentry. Environment: %s", self.environment)

    def zope_log(self):
        """ Zope logging
        """
        if self.mode == "zeo":
            return

        self.setup_graylog()
        self.setup_sentry()

    def zope_threads(self):
        """ Zope threads
        """
        if not self.threads:
            return

        self.conf = self.conf.replace('zserver-threads 2', 'zserver-threads %s' % self.threads)

    def zope_fast_listen(self):
        """ Zope fast-listen
        """
        if not self.fast_listen or self.fast_listen == 'off':
            return

        self.conf = self.conf.replace('fast-listen off', 'fast-listen %s' % self.fast_listen)

    def zope_force_connection_close(self):
        """ force-connection-close
        """
        if not self.force_connection_close or self.force_connection_close == 'on':
            return

        self.conf = self.conf.replace(
            'force-connection-close on', 'force-connection-close %s' % self.force_connection_close)

    def relstorage_host(self):
        """ RelStorage host
        """
        if not self.postgres_host:
            return

        self.conf = self.conf.replace("host='postgres'", "host='%s'" % self.postgres_host)

    def relstorage_user(self):
        """ RelStorage user
        """
        if not self.postgres_user:
            return

        self.conf = self.conf.replace("user='zope'", "user='%s'" % self.postgres_user)

    def relstorage_password(self):
        """ RelStorage password
        """
        if not self.postgres_password:
            return

        self.conf = self.conf.replace("password='zope'", "password='%s'" % self.postgres_password)

    def relstorage_keep_history(self):
        """ RelStorage keep-history
        """
        if self.keep_history:
            self.conf = self.conf.replace('keep-history false', 'keep-history true')

    def finish(self):
        conf = self.conf
        with open(self.zope_conf, 'w') as zfile:
            zfile.write(conf)

    def setup(self):
        """ Configure
        """
        super(Environment, self).setup()

        self.buildout()
        self.zope_mode()
        #self.zope_log()
        self.zope_threads()
        self.zope_fast_listen()
        self.zope_force_connection_close()
        self.relstorage_host()
        self.relstorage_user()
        self.relstorage_password()
        self.relstorage_keep_history()
        self.finish()

    __call__ = setup

BUILDOUT_TEMPLATE = """
[buildout]
extends = {buildout_extends}
find-links += {findlinks}
develop += {develop}
eggs += {eggs}
zcml += {zcml}

[instance]

[plonesite]
enabled = {enabled}
site-id = {site}
profiles += {profiles}

[versions]
{versions}

[sources]
{sources}
"""

GRAYLOG_TEMPLATE = """
  <graylog>
    server %s
    facility %s
  </graylog>
"""

def initialize():
    """ Configure
    """
    environment = Environment()
    environment.setup()

if __name__ == "__main__":
    initialize()
