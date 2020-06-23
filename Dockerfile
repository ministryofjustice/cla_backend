FROM alpine:3.9

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

COPY ./requirements ./requirements
RUN pip install -r ./requirements/production.txt

COPY . .

# Make sure static assets directory has correct permissions
RUN chown -R app:app /home/app && \
    mkdir -p cla_backend/assets

RUN python manage.py compilemessages

USER 1000
EXPOSE 8000

CMD ["docker/run.sh"]
