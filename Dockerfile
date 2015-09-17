#
# CLA_BACKEND Dockerfile all environments
#
# Pull base image.
FROM phusion/baseimage:0.9.11

MAINTAINER Peter Idah <peter.idah@digital.justice.gov.uk>

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

# Set timezone
RUN echo "Europe/London" > /etc/timezone  &&  dpkg-reconfigure -f noninteractive tzdata

# Remove SSHD
RUN rm -rf /etc/service/sshd /etc/my_init.d/00_regen_ssh_host_keys.sh

# Dependencies
RUN DEBIAN_FRONTEND='noninteractive' \
  apt-get update && \
  apt-get -y --force-yes install bash apt-utils python-pip python-dev build-essential git software-properties-common python-software-properties libpq-dev g++ make libpcre3 libpcre3-dev \
  libxslt-dev libxml2-dev && \
  apt-get -y build-dep python-psycopg2
# Install Nginx.
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:nginx/stable && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get -y --force-yes install nginx-full && \
  chown -R www-data:www-data /var/lib/nginx

ADD ./docker/nginx.conf /etc/nginx/nginx.conf
ADD ./docker/htpassword /etc/nginx/conf.d/htpassword
RUN rm -f /etc/nginx/sites-enabled/default && chown www-data:www-data /etc/nginx/conf.d/htpassword

# Pip install Python packages
RUN pip install -U setuptools pip wheel
RUN pip install GitPython uwsgi requests

RUN mkdir -p /var/log/wsgi && touch /var/log/wsgi/app.log /var/log/wsgi/debug.log && chown -R www-data:www-data /var/log/wsgi && chmod -R g+s /var/log/wsgi

RUN  mkdir -p /var/log/nginx/cla_backend
ADD ./docker/cla_backend.ini /etc/wsgi/conf.d/cla_backend.ini

# Define mountable directories.
VOLUME ["/data", "/var/log/nginx", "/var/log/wsgi"]

# APP_HOME
ENV APP_HOME /home/app/django

# Add requirements to docker
ADD ./requirements /tmp/requirements

# PIP INSTALL APPLICATION
RUN cd /tmp/requirements && pip install -r production.txt && find . -name '*.pyc' -delete

# Add project directory to docker
ADD . /home/app/django

RUN cd /home/app/django && cat docker/version >> /etc/profile

# PYCLEAN
RUN cd /home/app/django && find . -name '*.pyc' -delete

# install startup files for runit
ADD ./docker/migrations.startup /etc/my_init.d/migrations.startup

# install service files for runit
ADD ./docker/nginx.service /etc/service/nginx/run

# install service files for runit
ADD ./docker/uwsgi.service /etc/service/uwsgi/run

# install service files for runit
ADD ./docker/celery.service /etc/service/celery/run

#sym-link to local.py, which overrides all common settings.
RUN ln -s /home/app/django/cla_backend/settings/docker.py /home/app/django/cla_backend/settings/local.py

# Collect static
RUN cd /home/app/django && python manage.py collectstatic --noinput

# Compile messages
RUN cd /home/app/django && python manage.py compilemessages

# Expose ports.
EXPOSE 80

