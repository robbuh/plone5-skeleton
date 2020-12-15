# Plone-based generic fullstack development skeleton

A place to put common files used to develop Plone 5

The idea is to have a central place of useful code and configuration that can
provide a uniform developing experience. Stacks generated from this skeleton are not intended to be used in production, only for development. A production setup might be later provided as part of this skeleton.

## Based on:

- https://github.com/eea/eea.docker.plone
- https://github.com/eea/plone5-fullstack-skeleton/
- https://github.com/datakurre/gatsby-starter-plone-brochure

## Getting started on a new project

- Clone this repo `git clone https://github.com/robbuh/plone5-skeleton-ws`
- You can now run `make help` to see the available recipes.
- `make build-image` First build a new image. Image name is setted in `.env` file
- `make start-plone` Create new container for HAProxy, Zeoserver, Plone (Scaled in number of 4 ZEO clients), Memcached and start the Plone process.

### Developing for Plone image

After created or downloaded the custom image (ref. "Getting started on a new project" paragraph) start develop products and Plone image:

- `make setup-plone-dev` First setup a Plone develop environment. Just one plone container will be created. You can access to `@@reload` page to reload you custom product and you can access to many other development functionalities.
- `make plone-shell` to start a Plone docker container shell. This can be used to start the Plone instance manually, to debug code, or to rebuild the docker container buildout
- `make release-backend` to release a new version of the Plone docker image.

The boostrap process creates the `src` folder where the Plone development packages are.

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

After customized your products and edited your buildout rebuild docker image and test if everything is working in production

```
make build-image
make start-plone
```



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
