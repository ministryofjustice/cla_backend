#!/usr/bin/env bash
# This script does the following:
#   - Copies the current secret in diversity-keys to a previous-diversity-keys secret
#   - Puts the site into maintenance mode
#   - Removes the diversity-keys secret
#   - Re-creates the diversity-keys secret from the contents of the private and public key passed to it as arguments

# usage: <environment(uat,staging,training,production)> <path to private key file> <path to public key file>

set -e
echoerr() { echo "$@" 1>&2;exit; }

ENVIRONMENT=$1
PRIVATE_KEY_FILE=${2?param missing - private key file}
PUBLIC_KEY_FILE=${3?param missing public key file}
SECRET_NAME="diversity-keys"
BACKUP_SECRET_NAME="previous-diversity-keys"

if [ "$ENVIRONMENT" == "uat" ]; then
  NAMESPACE="laa-cla-backend-uat"
elif [ "$ENVIRONMENT" == "staging" ]; then
  NAMESPACE="laa-cla-backend-staging"
elif [ "$ENVIRONMENT" == "training" ]; then
  NAMESPACE="laa-cla-backend-training"
elif [ "$ENVIRONMENT" == "production" ]; then
  NAMESPACE="laa-cla-backend-production"
else
  echoerr "Invalid environment provided: $ENVIRONMENT"
  exit
fi

if [ "$ENVIRONMENT" == "production" ]; then
    echo "WARNING: YOU HAVE SELECTED A PRODUCTION NAMESPACE"
    read -p "ARE YOU SURE YOU WANT TO CONTINUE(YES/NO)" CONFIRM
    if [ "$CONFIRM" != "YES" ]; then
        echoerr "BYE"
        exit
    else
        read -p "RE-ENTER THE NAMESPACE YOU WOULD LIKE TO WORK ON(uat,staging,training,production)" CONFIRM_NAMESPACE
        if [ "$CONFIRM_NAMESPACE" != "production" ]; then
            echoerr "THE NAMESPACE YOU SUPPLIED($ENVIRONMENT) AND THE ONE YOU CONFIRMED($CONFIRM_NAMESPACE) DO NOT MATCH"
            exit
        fi
    fi
fi

if [ ! -f "$PRIVATE_KEY_FILE" ]; then
    echoerr "Private key file does not exist: $PRIVATE_KEY_FILE"
    exit
elif ! grep -q 'BEGIN PGP PRIVATE KEY BLOCK' $PRIVATE_KEY_FILE; then
    echoerr "$PRIVATE_KEY_FILE does not contain a private key"
    exit
elif [ ! -f $PUBLIC_KEY_FILE ]; then
    echoerr "Public key file does not exist: $PUBLIC_KEY_FILE"
    exit
elif ! grep -q 'BEGIN PGP PUBLIC KEY BLOCK' $PUBLIC_KEY_FILE; then
    echoerr "$PUBLIC_KEY_FILE does not contain a public key"
    exit
fi

echo "------------------------------------------------------------------------------------------"
echo "NAMESPACE: $NAMESPACE"
echo "SECRET NAME: $SECRET_NAME"
echo "BACKUP SECRET NAME: $BACKUP_SECRET_NAME"
echo "PRIVATE KEY FILE: $PRIVATE_KEY_FILE"
echo "PUBLIC KEY FILE: $PUBLIC_KEY_FILE"
read -p "ARE YOU SURE YOU WANT TO CONTINUE(YES/NO)" CONFIRM
if [ "$CONFIRM" != "YES" ]; then
    echoerr "BYE"
    exit
fi
echo "------------------------------------------------------------------------------------------"

kubens $NAMESPACE
BACKUP_SECRET_EXISTS=$(kubectl get --ignore-not-found secret $BACKUP_SECRET_NAME)
if [ "$BACKUP_SECRET_EXISTS" != "" ]; then
     echoerr "There is already a secret with the name $BACKUP_SECRET_NAME"
    exit
fi
echo "Backing up current key to file..."
CURRENT_KEY_FILENAME="diversity-current-key-$(date '+%Y-%m-%dT%H:%M:%S').key"
if [ -f $CURRENT_KEY_FILENAME ]; then
    echoerr "backup file already exists $CURRENT_KEY_FILENAME"
    exit
fi
CURRENT_KEY_FILENAME="diversity-current-key-$(date '+%Y-%m-%dT%H:%M:%S').key"
if [ -f $CURRENT_KEY_FILENAME ]; then
    echoerr "backup file already exists $CURRENT_KEY_FILENAME"
    exit
fi
CURRENT_SECRET_CONTENT=$(kubectl get secret $SECRET_NAME -o json)
if [ `command -v jq` ]; then
  CURRENT_SECRET_CONTENT=$(echo $CURRENT_SECRET_CONTENT | jq '.data|map_values(@base64d)' --raw-output)
fi
echo $CURRENT_SECRET_CONTENT > $CURRENT_KEY_FILENAME
echo "Saved contents of secret $SECRET_NAME to $CURRENT_KEY_FILENAME"

echo "Copying $SECRET_NAME secret to $BACKUP_SECRET_NAME secret"
KS_COMMAND="kubectl get secret $SECRET_NAME -o yaml |  sed -e '/uid:.*/d' -e '/resourceVersion: .*/d' -e '/creationTimestamp: .*/d' -e 's/name: $SECRET_NAME/name: $BACKUP_SECRET_NAME/g' | kubectl apply -f -"
echo "Running $KS_COMMAND"
eval $KS_COMMAND
echo "Dumping contents of backup secret $BACKUP_SECRET_NAME"
kubectl get secret $BACKUP_SECRET_NAME -o yaml

echo "------------------------------------------------------------------------------------------"
echo "Putting site into maintenance mode"
# Sometimes the vpn makes the maintenance mode script fail even if it has successfully put the site into maintenance mode
./bin/maintenance_mode.sh $ENVIRONMENT True || true

echo "Removing the old keys by deleting the secret $SECRET_NAME"
kubectl delete secret $SECRET_NAME
echo "Recreating $SECRET_NAME with new keys"
kubectl create secret generic $SECRET_NAME --from-file=private=$PRIVATE_KEY_FILE --from-file=public=$PUBLIC_KEY_FILE
echo "Restarting deployment so pods pickup new secret"
kubectl rollout restart deployment cla-backend-app
kubectl rollout restart deployment cla-backend-worker

