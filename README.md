# CLA Backend


[![CircleCI](https://circleci.com/gh/ministryofjustice/cla_backend/tree/master.svg?style=svg)](https://circleci.com/gh/ministryofjustice/cla_backend/tree/master)

[![Coverage Status](https://coveralls.io/repos/github/ministryofjustice/cla_backend/badge.svg?branch=master)](https://coveralls.io/github/ministryofjustice/cla_backend?branch=master)
    
Backend API for the Civil Legal Aid Tool.

## Dependencies

-  [Virtualenv](http://www.virtualenv.org/en/latest/)
-  Most recent version of pip
-  [Python 2.7](http://www.python.org/) (Can be installed with `brew install python2`)
-  [Postgres 9.4+](http://www.postgresql.org/)

## Installation

Clone the repository:

    git clone git@github.com:ministryofjustice/cla_backend.git

Next, create the development environment and start it up:

    ./run_local.sh

## Lint and pre-commit hooks

To lint with Black and flake8, install pre-commit hooks:
```
. env/bin/activate
pip install -r requirements/dev.txt
pre-commit install
```

To run them manually:
```
pre-commit run --all-files
```

## Environments

To setup the development environment you will need to run:

    ./run_local.sh

To setup test or production environments, you will need to specify which one you want to run ie:

    ./run_local.sh test

## Debug mode

To enter debug mode, ensure you have setup your dev environment `./run_local.sh`

Add `import pdb` and `pdb.set_trace()` wherever you want to trigger the debugger in the codebase.

You will then need to get the cla_backend docker container id from `docker ps`

Now run `docker attach CONTAINERID` where CONTAINERID is taken from the previous step.

## Translations

When making changes to text (e.g. GraphML files) translations should be updated. To update translations run:

     ./manage.py translations update

Or on macOS ~10.14

    brew install gettext
    PATH="/usr/local/opt/gettext/bin:$PATH" ./manage.py translations update

Using the a Transifex account that has been added as a Project maintainer to the `cla_public` project,
fetch an API token from https://www.transifex.com/user/settings/api/

Create `~/.transifexrc` in the following format and insert the API token:

    [https://www.transifex.com]
    api_hostname = https://api.transifex.com
    hostname = https://www.transifex.com
    password = INSERT_API_TOKEN_HERE
    username = api

Then `./manage.py translations push` to Transifex and `./manage.py translations pull` when complete.


## Scope Graphs

* Edit the .graphml files, e.g. using a tool like [yEd](http://www.yworks.com/en/products/yfiles/yed/), to change the scope diagnosis trees
* Run Django management command `python manage.py translations update` to update translations and templated graph files

See more detailed instructions in the [how-to guide](https://dsdmoj.atlassian.net/wiki/spaces/laagetaccess/pages/1005060261/Produce+diagram+of+CLA+merits+decision+tree) on Confluence (log-in required).


## Troubleshooting

If you are experiencing errors when creating and syncing the database, make sure the following are added to your `PATH` var (amend path to postgres as necessary):

    export PATH="/Applications/Postgres.app/Contents/Versions/9.4/bin/:$PATH"
    export DYLD_LIBRARY_PATH="/Applications/Postgres.app/Contents/Versions/9.4/lib/:$DYLD_LIBRARY_PATH"

If you get the error `django.db.utils.OperationalError: FATAL:  role "postgres" does not exist`, you will need to create the user `postgres` on the database. Run this from the command line (not in psql).

    createuser -s -e postgres

If you get the error `CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.` then set up a DEBUG environment variable. The easiest way to do this is to add the following line to settings/local.py

    DEBUG = True

## Releasing

Please make sure you tested on a non-production environment before merging.

This process now runs entirely through CircleCI. There are manual approvals required but the process can be run at any time of the day and through working hours.

1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/cla_backend) for the feature branch associated with the pull request. 
1. If the branch passes CircleCI then ask for the pull request to be approved then merge the pull request into the main github branch.
1. Once the merge is complete then go to CircleCI to check jobs are progressing on the main branch. Note that there is a job called static_uat_deploy_approval - this does not need to be approved unless your change requires this.
1. CircleCI will stop and wait for manual approval at 'staging_deploy_approval'. Proceed with approval (click on the thumb icon) if all  prior jobs have successfully completed.
1. Once the staging jobs have finished then check that the staging server is running correctly. The url will be in the slack message associated with the most recent job in cla-notifications.
1. if staging is not working then any changes should be rolled back and the feature checked. If staging is working correctly then manually approve production_deploy_approval.
1. Everything should pass and complete. If you haven't approved static_uat_deploy_approval then the pipeline will show on hold - this is ok.
