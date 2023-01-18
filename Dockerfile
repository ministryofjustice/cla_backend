#################################################
# BASE IMAGE USED BY ALL STAGES
#################################################
FROM alpine:3.9 as base

RUN apk add --no-cache \
      bash \
      py2-pip \
      tzdata \
      gettext

RUN adduser -D app && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

# To install pip dependencies
RUN apk add --no-cache \
      build-base \
      curl \
      git \
      libxml2-dev \
      libxslt-dev \
      linux-headers \
      postgresql-dev \
      python2-dev && \
    pip install -U setuptools pip==18.1 wheel

WORKDIR /home/app

COPY ./requirements/generated/ ./requirements

#################################################
# DEVELOPMENT
#################################################

FROM base AS development

# additional package required otherwise build of coveralls fails
RUN apk add --no-cache libffi-dev
RUN pip install -r ./requirements/requirements-dev.txt --no-cache-dir
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

ARG specific_test_input=""
ENV specific_test $specific_test_input

USER 1000
CMD ["sh", "-c", "./manage.py test $specific_test"]


#################################################
# PRODUCTION
#################################################
FROM base AS production

# Make sure static assets directory has correct permissions
RUN pip install -r ./requirements/requirements-production.txt --no-cache-dir
COPY . .

# Make sure static assets directory has correct permissions
RUN chown -R app:app /home/app && \
    mkdir -p cla_backend/assets

RUN python manage.py compilemessages
USER 1000
EXPOSE 8000
CMD ["docker/run.sh"]



