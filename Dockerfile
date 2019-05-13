FROM alpine:3.9

RUN apk add --no-cache \
      bash \
      gettext \
      nginx \
      py2-pip \
      supervisor \
      tzdata \
      uwsgi

# To install pip dependencies
RUN apk add --no-cache \
      build-base \
      git \
      libxml2-dev \
      libxslt-dev \
      postgresql-dev \
      python2-dev

RUN cp /usr/share/zoneinfo/Europe/London /etc/localtime
RUN pip install -U setuptools pip==18.1 wheel

ENV APP_HOME /home/app/django
COPY ./requirements /tmp/requirements
RUN cd /tmp/requirements && pip install -r production.txt

COPY ./docker/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/htpassword /etc/nginx/conf.d/htpassword
COPY ./docker/supervisord-services.ini /etc/supervisor.d/

RUN mkdir -p /var/log/nginx/cla_backend /var/log/wsgi /var/run/celery /var/log/celery && \
    touch /var/log/wsgi/app.log /var/log/wsgi/debug.log && \
    chmod -R g+s /var/log/wsgi

RUN adduser -D www-data -G www-data && \
    chown -R www-data:www-data /var/log/uwsgi /var/log/nginx/cla_backend && \
    chmod -R g+s /var/log/wsgi

WORKDIR /home/app/django
COPY . .

RUN ln -s /home/app/django/cla_backend/settings/docker.py /home/app/django/cla_backend/settings/local.py

RUN python manage.py collectstatic --noinput && \
    python manage.py compilemessages

EXPOSE 80

ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["supervisord", "--nodaemon"]
