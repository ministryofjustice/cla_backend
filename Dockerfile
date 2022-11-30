FROM alpine:3.15

RUN apk add --no-cache \
    bash \
    curl \
    tzdata \
    gettext \
    python2-dev \
    libffi-dev

RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
RUN python get-pip.py

RUN adduser -D app && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

# To install pip dependencies
RUN apk add --no-cache \
    build-base \
    git \
    libxml2-dev \
    libxslt-dev \
    linux-headers \
    postgresql-dev

RUN pip install -U setuptools pip wheel

WORKDIR /home/app

COPY ./requirements/generated/ ./requirements
RUN pip install -r ./requirements/requirements-production.txt --no-cache-dir

COPY . .

# Make sure static assets directory has correct permissions
RUN chown -R app:app /home/app && \
    mkdir -p cla_backend/assets

RUN python manage.py compilemessages

USER 1000
EXPOSE 8000

CMD ["docker/run.sh"]
