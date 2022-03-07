FROM python:3.7-alpine3.12
RUN apk add \
      bash \
      build-base \
      wget \
      postgresql-client \
      postgresql-dev \
      python3-dev \
      tzdata \
      screen

RUN adduser -D app && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

RUN pip install psycopg2==2.7.5

USER 1000
WORKDIR /home/app

COPY migration.sh .
COPY migration_validation.py .

ENTRYPOINT ["tail", "-f", "/dev/null"]

