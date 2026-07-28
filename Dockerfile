#################################################
# BASE IMAGE USED BY ALL STAGES
#################################################
FROM alpine:3.20 AS base

RUN apk add --no-cache \
      bash \
      tzdata \
      gettext

RUN adduser -D app && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

# Alpine's Python is "externally managed" (PEP 668); allow pip to install
# packages system-wide inside this container image.
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Install Python 3 build/runtime dependencies and modern packaging tools.
RUN apk add --no-cache \
      build-base \
      curl \
      curl-dev \
      git \
      libxml2-dev \
      libxslt-dev \
      linux-headers \
      postgresql-dev \
            python3 \
            python3-dev \
            py3-pip \
      libffi-dev \
      openssl-dev && \
        python3 -m pip install --upgrade pip wheel && \
        python3 -m pip install 'setuptools==80.9.0'
# setuptools is pinned (not upgraded) to match requirements-base.in: newer
# releases drop the bundled pkg_resources module that some dependencies
# (e.g. django-nested-admin) still import at runtime.


WORKDIR /home/app

COPY ./requirements/generated/ ./requirements

RUN python3 -m pip install 'PyYAML==6.0.2'

#################################################
# DEVELOPMENT
#################################################

FROM base AS development

# additional package required otherwise build of coveralls fails
RUN apk add --no-cache libffi-dev

RUN python3 -m pip install -r ./requirements/requirements-dev.txt --no-cache-dir
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
RUN python3 -m pip install -r ./requirements/requirements-production.txt --no-cache-dir
COPY . .

# Make sure static assets directory has correct permissions
RUN chown -R app:app /home/app && \
    mkdir -p cla_backend/assets

RUN python3 manage.py compilemessages
USER 1000
EXPOSE 8000
CMD ["docker/run.sh"]



