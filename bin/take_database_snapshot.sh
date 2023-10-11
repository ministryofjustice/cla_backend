#!/bin/sh -e
NAMESPACE=$1
K8S_RDS_SECRET=$2
if [ -z "${NAMESPACE}" ]; then
	echo "Please provide namespace argument"
	exit
fi
if [ -z "${K8S_RDS_SECRET}" ]; then
	echo "Please provide the name of your rds secret"
	exit
fi
export AWS_ACCESS_KEY_ID=`kubectl -n $NAMESPACE get secret $K8S_RDS_SECRET -o json | jq '.data|map_values(@base64d).access_key_id' --raw-output`
export AWS_SECRET_ACCESS_KEY=`kubectl -n $NAMESPACE get secret $K8S_RDS_SECRET -o json | jq '.data|map_values(@base64d).secret_access_key' --raw-output`
export AWS_DEFAULT_REGION=eu-west-2

DB_IDENTIFIER=`kubectl -n $NAMESPACE get secret $K8S_RDS_SECRET -o json | jq '.data|map_values(@base64d).db_identifier' --raw-output`
BACKUP_NAME="MANUAL-BACKUP-`date +%s`"

echo "NAMESPACE: $NAMESPACE"
echo "ACCESS_KEY: $AWS_ACCESS_KEY_ID"
echo "SECRET_KEY: $AWS_SECRET_ACCESS_KEY"
echo "DB_IDENTIFIER: $DB_IDENTIFIER"
echo "BACKUP_NAME: $BACKUP_NAME"

echo "Creating backup now"
RESPONSE=`aws rds create-db-snapshot --db-instance-identifier $DB_IDENTIFIER --db-snapshot-identifier $BACKUP_NAME`
echo "Checking status of snapshot"
STATUS=`echo $RESPONSE | jq '.DBSnapshot.Status' --raw-output`
while [[ $STATUS != "available" ]]; do
	echo "Status is $STATUS...waiting 30 seconds before checking status again"
	sleep 30
	STATUS=`aws rds describe-db-snapshots --db-instance-identifier $DB_IDENTIFIER --db-snapshot-identifier $BACKUP_NAME | jq '.DBSnapshots[0].Status' --raw-output`
done
echo "Finished with status: $STATUS"
