#!/bin/bash
set -e

# check if environment variables exist
# variable names
#
TARGET_DB_HOST='localhost'
TARGET_DB_NAME='cla_backend_target2'
TARGET_DB_USER='postgres'
TARGET_DB_PASS=''

if PGPASSWORD=$TARGET_DB_PASS psql \
-U $TARGET_DB_USER \
-h $TARGET_DB_HOST \
-lqt | cut -d \| -f 1 | grep -qw $TARGET_DB_NAME;
then
  echo 'Target exists'
else
  echo 'Could not connect to target'
  exit 1
fi

SOURCE_DB_HOST='localhost'
SOURCE_DB_NAME='cla_backend'
SOURCE_DB_USER='postgres'
SOURCE_DB_PASS=''

if PGPASSWORD=$SOURCE_DB_PASS psql \
-U $SOURCE_DB_USER \
-h $SOURCE_DB_HOST \
-lqt | cut -d \| -f 1 | grep -qw $SOURCE_DB_NAME;
then
  echo 'Source exists'
else
  echo 'Could not connect to source'
  exit 1
fi

echo 'Dumping source database...'
PGPASSWORD=$SOURCE_DB_PASS pg_dump -c -U $SOURCE_DB_USER \
     -h $SOURCE_DB_HOST \
     -d $SOURCE_DB_NAME \
     > database.sql

echo 'Restoring to target database...'
PGPASSWORD=$TARGET_DB_PASS psql -U $TARGET_DB_USER \
     -h $TARGET_DB_HOST \
     -d $TARGET_DB_NAME \
     -f database.sql 2> errors.txt
cat errors.txt

# echo 'Dumping sequences...'
# PGPASSWORD=$SOURCE_DB_PASS pg_dump -U $SOURCE_DB_USER \
#      -h $SOURCE_DB_HOST \
#      -d $SOURCE_DB_NAME \
#      -t '*_seq' > sequences.sql

# echo 'Dumping data...'
# PGPASSWORD=$SOURCE_DB_PASS pg_dump -U $SOURCE_DB_USER \
#      -h $SOURCE_DB_HOST \
#      -d $SOURCE_DB_NAME \
#      -O \
#      --section=data > data.sql

# echo 'Dumping post-data...'
# PGPASSWORD=$SOURCE_DB_PASS pg_dump -U $SOURCE_DB_USER \
#      -h $SOURCE_DB_HOST \
#      -d $SOURCE_DB_NAME \
#      -O \
#      --section=post-data > post-data.sql


# echo 'Starting restore process'


# echo 'Doing restore pre-data'
# PGPASSWORD=$TARGET_DB_PASS psql -U $TARGET_DB_USER \
#      -h $TARGET_DB_HOST \
#      -d $TARGET_DB_NAME \
#      -f pre-data.sql

# echo 'Doing restore sequences'
# PGPASSWORD=$TARGET_DB_PASS psql -U $TARGET_DB_USER  \
#      -h $TARGET_DB_HOST \
#      -d $TARGET_DB_NAME \
#      -f sequences.sql

# echo 'Doing restore data'
# PGPASSWORD=$TARGET_DB_PASS psql -U $TARGET_DB_USER \
#      -h $TARGET_DB_HOST \
#      -d $TARGET_DB_NAME \
#      -f data.sql

# echo 'Doing restore post-data'
# PGPASSWORD=$TARGET_DB_PASS psql -U $TARGET_DB_USER \
#      -h $TARGET_DB_HOST \
#      -d $TARGET_DB_NAME \
#      -f post-data.sql
