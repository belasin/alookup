FROM python:2-alpine
MAINTAINER Justin Unwin <junwin@gmail.com>

RUN apk add bash
RUN apk add --no-cache tzdata
ENV TZ Africa/Johannesburg

RUN apk add --no-cache python2-dev
RUN ln -sf /usr/lib/python2.7/site-packages/* /usr/local/lib/python2.7/site-packages/

RUN pip install 'plaster_pastedeploy' 'pyramid' 'pyramid_debugtoolbar' 'pyramid_beaker' 'waitress' 'requests'

RUN mkdir /alookup
RUN mkdir /alookup-dist
RUN mkdir /alookup-dist/pims-src

WORKDIR /pims/alookup-src

ADD . .

RUN pip install .

WORKDIR /alookup

ENV PATH="/alookup:/alookup/bin:${PATH}"

RUN cp /alookup/alookup-src/docker/entry.sh /alookup/
RUN chmod a+x /alookup/entry.sh

RUN rm -fr /pims/alookup-src

RUN rm -fr /root/.cache

RUN mkdir -p /alookup/configs
RUN mkdir -p /alookup/run
RUN mkdir -p /alookup/data
RUN mkdir -p /alookup/logs

VOLUME ["/alookup/config", "/alookup/logs", "/alookup/export"]

EXPOSE 8080

ENTRYPOINT ["/alookup/entry.sh"]

CMD ["serve"]