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

# Dependencies
RUN DEBIAN_FRONTEND='noninteractive' \ 
  apt-get update && \
  apt-get -y --force-yes install apt-utils python-pip python-dev build-essential git software-properties-common python-software-properties libpq-dev g++ make libpcre3 libpcre3-dev && \
  apt-get -y build-dep python-psycopg2
# Install Nginx.
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:nginx/stable && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get -y --force-yes install nginx-full && \
  chown -R www-data:www-data /var/lib/nginx

ADD ./docker/nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/sites-enabled/default

# Install ruby
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:brightbox/ruby-ng && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get install -y --no-install-recommends  ruby2.1 ruby2.1-dev

RUN gem2.1 install sass --no-rdoc --no-ri

#Pip install Python packages

RUN pip install GitPython uwsgi

RUN mkdir -p /var/log/wsgi && touch /var/log/wsgi/app.log /var/log/wsgi/debug.log && chown -R www-data:www-data /var/log/wsgi && chmod -R g+s /var/log/wsgi

RUN  mkdir -p /var/log/nginx/cla_backend
ADD ./docker/cla_backend.ini /etc/wsgi/conf.d/cla_backend.ini

# Define mountable directories.
VOLUME ["/data", "/var/log/nginx", "/var/log/wsgi"]

# APP_HOME
ENV APP_HOME /home/app/django

# Add project directory to docker
ADD . /home/app/django

# PIP INSTALL APPLICATION
RUN cd /home/app/django && pip install -r requirements/production.txt && find . -name '*.pyc' -delete

# install service files for runit
ADD ./docker/nginx.service /etc/service/nginx/run

# install service files for runit
ADD ./docker/uwsgi.service /etc/service/uwsgi/run

ADD ./docker/rc.local /etc/rc.local

# Expose ports.
EXPOSE 80
