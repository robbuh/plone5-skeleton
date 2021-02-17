FROM plone:5.2.2-python37

RUN mv /docker-entrypoint.sh /plone-entrypoint.sh \
 && mv /docker-initialize.py /plone_initialize.py \
 && mv /plone/instance/buildout.cfg /plone/instance/plone-buildout.cfg \
 && mv /plone/instance/develop.cfg /plone/instance/plone-develop.cfg
 
# Websocket - comment cryptography from [versions] section
#RUN sed -i "s/cryptography/#cryptography/g" /plone/instance/plone-buildout.cfg

COPY config/docker/* /
COPY config/plone/* /plone/instance/
RUN /docker-setup.sh
