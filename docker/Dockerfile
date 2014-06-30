#
# CLA Dockerfile
#
# https://github.com/dockerfile/nginx
#
# Pull base image.
FROM phusion/baseimage:0.9.10

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

ADD ./nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/sites-enabled/default

# Install ruby
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:brightbox/ruby-ng && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get install -y --no-install-recommends  ruby2.1 ruby2.1-dev

RUN gem2.1 install sass --no-rdoc --no-ri

#Pip install Python packages

RUN pip install GitPython uwsgi

RUN mkdir -p /var/log/wsgi

RUN  mkdir -p /var/log/nginx/cla_backend
ADD ./cla_backend.ini /etc/wsgi/conf.d/cla_backend.ini

# Define mountable directories.
VOLUME ["/data", "/var/log/nginx", "/var/log/wsgi"]

# APP_HOME
ENV APP_HOME /home/app/django

# Add project directory to docker
ADD ./ /home/app/django

# Add deploy-key
RUN mkdir -p /root/.ssh
ADD ./deploy-key /root/.ssh/id_rsa
ADD ./config /root/.ssh/config

# Add local.py for QA
ADD ./local.py /home/app/django/cla_backend/settings/local.py

# Define working directory.
WORKDIR /home/app/django

# PIP INSTALL APPLICATION
RUN pip install -r requirements/production.txt

# Create django super-user and password
#echo "from django.contrib.auth.models import User; User.objects.create_superuser('pidah','peter.idah@digital.justice.gov.uk', 'S3cur31sh')" | ./manage.py shell

# Manage sync db
RUN python manage.py syncdb --noinput

# manage syncdb migrate
RUN python manage.py migrate

RUN python manage.py loaddata initial_category.json

RUN python manage.py collectstatic --noinput

# install service files for runit
ADD nginx.service /etc/service/nginx/run

# install service files for runit
ADD uwsgi.service /etc/service/uwsgi/run

# Expose ports.
EXPOSE 80
