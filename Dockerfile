#################################################
# BASE IMAGE USED BY ALL STAGES
#################################################
FROM alpine:3.9 as base

RUN apk add --no-cache \
      bash \
      py2-pip \
      tzdata \
      gettext

RUN adduser -D app
RUN cp /usr/share/zoneinfo/Europe/London /etc/localtime
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

# Make sure static assets directory has correct permissions
RUN chown -R app:app /home/app && \
    mkdir -p cla_backend/assets

#################################################
# DEVELOPMENT
#################################################

FROM base AS development

# additional package required otherwise build of coveralls fails
RUN apk add --no-cache libffi-dev
RUN pip install -r ./requirements/requirements-dev.txt --no-cache-dir
COPY . .
EXPOSE 8000
CMD ["docker/run_dev.sh"]

#################################################
# TEST
#################################################
FROM development AS test

CMD ["./manage.py", "test"]

#################################################
# PRODUCTION
#################################################
FROM base AS production

RUN pip install -r ./requirements/requirements-production.txt --no-cache-dir

COPY . .
RUN python manage.py compilemessages
USER 1000
EXPOSE 8000
CMD ["docker/run.sh"]



