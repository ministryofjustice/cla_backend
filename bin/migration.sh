#!/bin/bash
set -e

# Make sure we can connect to the target database
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

# Make sure we can connect to the source database
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

# Clear out the old database
PGPASSWORD=$TARGET_DB_PASS psql -d $TARGET_DB_NAME -c 'drop schema public cascade;create schema public;'

##################################################################################################################
# Dump the source database
##################################################################################################################
PGPASSWORD=$SOURCE_DB_PASS pg_dump -U $SOURCE_DB_USER \
      -h $SOURCE_DB_HOST \
      -d $SOURCE_DB_NAME \
      -O \
     --section=pre-data > pre-data.sql

 echo 'Dumping data...'
 PGPASSWORD=$SOURCE_DB_PASS pg_dump -U $SOURCE_DB_USER \
      -h $SOURCE_DB_HOST \
      -d $SOURCE_DB_NAME \
      -O \
      --section=data > data.sql

 echo 'Dumping post-data...'
 PGPASSWORD=$SOURCE_DB_PASS pg_dump -U $SOURCE_DB_USER \
      -h $SOURCE_DB_HOST \
      -d $SOURCE_DB_NAME \
      -O \
      --section=post-data > post-data.sql


##################################################################################################################
# Restore the target database
##################################################################################################################
 echo 'Doing restore pre-data'
 PGPASSWORD=$TARGET_DB_PASS psql -U $TARGET_DB_USER \
      -h $TARGET_DB_HOST \
      -d $TARGET_DB_NAME \
      -f pre-data.sql \
      2>> errors.txt 1>> output.txt

 echo 'Doing restore data'
 PGPASSWORD=$TARGET_DB_PASS psql -U $TARGET_DB_USER \
      -h $TARGET_DB_HOST \
      -d $TARGET_DB_NAME \
      -f data.sql \
      2>> errors.txt 1>> output.txt

 echo 'Doing restore post-data'
 PGPASSWORD=$TARGET_DB_PASS psql -U $TARGET_DB_USER \
      -h $TARGET_DB_HOST \
      -d $TARGET_DB_NAME \
      -f post-data.sql \
      2>> errors.txt 1>> output.txt
