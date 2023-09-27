#################################################
# BASE IMAGE USED BY ALL STAGES
#################################################
FROM alpine:3.15 as base

RUN apk add --no-cache \
      bash \
      tzdata \
      gettext

RUN adduser -D app && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

# To install pip dependencies
# python -m ensurepip --upgrade -- installs pip version 19
#  pip install -U setuptools pip==18.1 wheel -- ensures pip is at version 18
RUN apk add --no-cache \
      build-base \
      curl curl-dev \
      git \
      libxml2-dev \
      libxslt-dev \
      linux-headers \
      postgresql-dev \
      python2-dev && \
      python -m ensurepip --upgrade && \
      pip install -U setuptools pip==18.1 wheel

WORKDIR /home/app

COPY ./requirements/generated/ ./requirements

# cython pyyaml bug requires fixing cython to <3.0 otherwise pyyaml won't build
RUN echo 'Cython < 3.0' > /tmp/constraint.txt
RUN PIP_CONSTRAINT=/tmp/constraint.txt pip install 'PyYAML==5.4.1'

#################################################
# DEVELOPMENT
#################################################

FROM base AS development

# additional package required otherwise build of coveralls fails
RUN apk add --no-cache libffi-dev

RUN PIP_CONSTRAINT=/tmp/constraint.txt pip install -r ./requirements/requirements-dev.txt --no-cache-dir
COPY . .

# Make sure static assets directory has correct permissions
RUN chown -R app:app /home/app && \
    mkdir -p cla_backend/assets

USER 1000
EXPOSE 8000
CMD ["docker/run_dev.sh"]

#################################################
# TEST
#################################################
FROM development AS test

USER 1000
CMD ["./manage.py", "test"]


#################################################
# PRODUCTION
#################################################
FROM base AS production

# Make sure static assets directory has correct permissions
RUN PIP_CONSTRAINT=/tmp/constraint.txt pip install -r ./requirements/requirements-production.txt --no-cache-dir
COPY . .

# Make sure static assets directory has correct permissions
RUN chown -R app:app /home/app && \
    mkdir -p cla_backend/assets

RUN python manage.py compilemessages
USER 1000
EXPOSE 8000
CMD ["docker/run.sh"]



