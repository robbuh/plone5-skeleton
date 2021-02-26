# Run a new plone instance
docker run --rm --name plone -p 8080:8080 robbuh/plone:5.2.2-python37

# Test of ENV vars
docker run --rm \
-v $(PWD)/config/docker/docker-initialize.py:/docker-initialize.py \
-v $(PWD)/src/:/plone/instance/src/ \
-p 8080:8080 -e SITE=plone \
-e ADDONS="plonetheme.gruezibuesi" \
-e VERSIONS="" \
-e DEVELOP="src/plonetheme.gruezibuesi" \
-e SOURCES="plonetheme.gruezibuesi = git https://github.com/collective/plonetheme.gruezibuesi" \
robbuh/plone:5.2.2-python37

# Develop new buildout products
docker run --rm --name plone -p 8080:8080 \
-v $(PWD)/config/docker/docker-initialize.py:/docker-initialize.py \
-v $(PWD)/src/:/plone/instance/src/ \
-v $(PWD)/config/plone/site.cfg:/plone/instance/site.cfg \
-v $(PWD)/config/plone/sources.cfg:/plone/instance/sources.cfg \
robbuh/plone:5.2.2-python37

# Run Plone with zeo
docker run --link=zeo --rm --name plone -p 8080:8080 \
-v $(PWD)/config/docker/docker-initialize.py:/docker-initialize.py \
-v $(PWD)/src/:/plone/instance/src/ \
-v $(PWD)/config/plone/site.cfg:/plone/instance/site.cfg \
-v $(PWD)/config/plone/sources.cfg:/plone/instance/sources.cfg \
-e ZOPE_MODE=zeo_client \
robbuh/plone:5.2.2-python37

# Connect to container
docker exec -it plone /bin/bash
# Run buildout on container
docker exec plone buildout -c buildout.cfg
