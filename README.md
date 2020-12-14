# Plone-based generic fullstack development skeleton

A place to put common files used to develop Plone 5

The idea is to have a central place of useful code and configuration that can
provide a uniform developing experience. Stacks generated from this skeleton are not intended to be used in production, only for development. A production setup might be later provided as part of this skeleton.

Based on:

- https://github.com/eea/eea.docker.plone
- https://github.com/eea/plone5-fullstack-skeleton/
- https://github.com/datakurre/gatsby-starter-plone-brochure

## Getting started on a new project

1. Clone this repo
2. Clone https://github.com/robbuh/plone5-skeleton-ws under folder "frontend"
3. Adjust image and package names in all files.


You can now run `make help` to see the recipes that you have available.

Each developer that will work on the project needs to execute (after they clone your development repo) one of the following bootstrap targets, according to their role:

- backend, run `make setup-plone-dev`
- frontend, run `make setup-frontend-dev`
- fullstack, run `make setup-fullstack-dev`. This executes both previous bootstraps and enables developing for both frontend and backend targets.

### Developing for Plone image

- `make build-image` First build a new image. Image's name is setted in .env files
- `make start-plone` Start the Plone process. This create new container for HAProxy (port::1936), Zeoserver, Plone (Scaled in number of 4 ZEO clients), Memcached

The backend boostrap process creates the `src` folder where the Plone development packages are. Some useful commands are:

- `make plone-shell` to start a Plone docker container shell. This can be used to start the Plone instance manually, to debug code, or to rebuild the docker container buildout
- `make release-backend` to release a new version of the Plone docker image.

To create a new addon, you can run something like this: (please adjust according to intended package name and your user uid on the host machine - 1000 is usually the default on desktop Linux distributions, but there's no standard).

```
pip install bobtemplates.plone
mrbob bobtemplates.plone:addon -O src/eea.mynewpkg
cd src/eea.mynewpkg
mrbob bobtemplates.plone:content_type
cd -
chown -R 1000 src
```

The `config/plone/site.cfg` file is mapped as a docker volume. If you change this file, the plone container needs to be restarted:

```
make shell
docker-compose restart plone
```
If you brind new development packages, you need to fix permissions in the `src/` folder, by running (in bash):
```
sudo chown -R `whoami` src/
```

If you use fish as a shell, run:

```
sudo chown -R (whoami) src/
```

## Keep your project updated to the common skeleton

To keep up to date with it run:

```
make sync-makefiles
```
