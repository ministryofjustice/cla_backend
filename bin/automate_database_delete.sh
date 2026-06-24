#!/bin/sh

deleteManualSnapShot() {

    echo "Logging into RDS"

    regex_manual='cla-backend-manual-snapshot'
    regex_automatic='rds:cloud-platform'

    regex_identifer='\..*'
    SNAPSHOT_TO_KEEP=24

    manual_snapshots=$(aws rds describe-db-snapshots --region=eu-west-2 --db-instance-identifier $DB_IDENTIFIER \
                    | jq -r '.DBSnapshots[] | "\(.DBSnapshotIdentifier)"' | grep $regex_manual )

    snapshot_count=$(aws rds describe-db-snapshots --region=eu-west-2 --db-instance-identifier $DB_IDENTIFIER \
                    | jq -r '.DBSnapshots[] | "\(.DBSnapshotIdentifier)"' | grep $regex_automatic | wc -l)

    array=($manual_snapshots)

    echo 'There are' ${#array[@]} 'hourly backups'
    echo 'There are' $snapshot_count 'automatic daily DB backups'

    if [ ${#array[@]} -gt $SNAPSHOT_TO_KEEP ]
    then
        END=$((${#array[@]} - $SNAPSHOT_TO_KEEP ))
        for ((i=0;i<=$END;++i)); do (aws rds delete-db-snapshot --region=eu-west-2 --db-snapshot-identifier ${array[i]}) ; done
    else
        echo "No need to delete any backups today"
    fi

}

deleteManualSnapShot() 