#!/bin/sh

current_time=$(date "+%Y%m%d-%H%M")
file_name="cla-backend-manual-snapshot"

new_fileName=$file_name-$current_time

aws rds create-db-snapshot --region=eu-west-2 --db-instance-identifier $DB_IDENTIFIER --db-snapshot-identifier $new_fileName
