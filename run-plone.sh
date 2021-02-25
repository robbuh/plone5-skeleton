docker run --rm \
-v $(PWD)/config/docker/docker-initialize.py:/docker-initialize.py \
-v $(PWD)/src/:/plone/instance/src/ \
-p 8080:8080 -e SITE=plone \
-e ADDONS="collective.easyform" \
-e VERSIONS="collective.easyform=3.0.5" \
-e DEVELOP="src/plonetheme.gruezibuesi" \
-e SOURCES="plonetheme.gruezibuesi = git https://github.com/collective/plonetheme.gruezibuesi" \
robbuh/plone:5.2.2-python37
