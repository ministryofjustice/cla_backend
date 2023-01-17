# CLA Backend


[![CircleCI](https://circleci.com/gh/ministryofjustice/cla_backend/tree/master.svg?style=svg)](https://circleci.com/gh/ministryofjustice/cla_backend/tree/master)

[![Coverage Status](https://coveralls.io/repos/github/ministryofjustice/cla_backend/badge.svg?branch=master)](https://coveralls.io/github/ministryofjustice/cla_backend?branch=master)
    
Backend API for the Civil Legal Aid Tool.

## Installation

############################################################### 
Local installation for development purposes

The Dockerfile that is used to create the image for production
is used to create a development docker container

It is a multistage dockerfile with three stages for
 - development
 - test
 - production
 - 
###############################################################

Clone the repository:

    git clone git@github.com:ministryofjustice/cla_backend.git

## Development Container

If no stage is passed to the run_local.sh script then it will default to development

Start up the development docker container:

    ./run_local.sh

You can connect to the fox admin application from http://localhost:8010/admin and log in as cla_admin

## Debugging

Once you have created your docker development container as above. 

Add `import pdb` and `pdb.set_trace()` wherever you want to trigger the debugger in the codebase.

You will then need to get the cla_backend docker container id from `docker ps`

Now run `docker attach CONTAINERID` where CONTAINERID is taken from the previous step.

When pdb.set_trace() is reached, you will be able to debug from the command line.

`https://docs.python.org/3/library/pdb.html`

## Unit tests

To run unit tests, this could be done from within the devlopment container or you could run:

    ./run_local.sh test

## Lint and pre-commit hooks

To lint with Black and flake8, install pre-commit hooks:

```
virtualenv -p python2.7 env --prompt=\(cla_be\)
. env/bin/activate
pip install -r ./requirements/requirements-lint.txt
pre-commit install
```

To run them manually:
```
pre-commit run --all-files
```

NB Old Macbooks no longer have python 2.7 installed. 
If you want to install a 2.7 virtualenv then use pyenv-virtualenv
https://github.com/pyenv/pyenv-virtualenv

## Releasing to production

Please make sure you tested on a non-production environment before merging.

This process now runs entirely through CircleCI. There are manual approvals required but the process can be run at any time of the day and through working hours.

1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/cla_backend) for the feature branch associated with the pull request. 
2. If the branch passes CircleCI then ask for the pull request to be approved then merge the pull request into the main github branch.
3. Once the merge is complete then go to CircleCI to check jobs are progressing on the main branch. Note that there is a job called static_uat_deploy_approval - this does not need to be approved unless your change requires this.
4. CircleCI will stop and wait for manual approval at 'staging_deploy_approval'. Proceed with approval (click on the thumb icon) if all  prior jobs have successfully completed.
5. Once the staging jobs have finished then check that the staging server is running correctly. The url will be in the slack message associated with the most recent job in cla-notifications.
6. if staging is not working then any changes should be rolled back and the feature checked. If staging is working correctly then manually approve production_deploy_approval.
7. Everything should pass and complete. If you haven't approved static_uat_deploy_approval then the pipeline will show on hold - this is ok.

###############################################################
## From here is not usually required and/or maintained
###############################################################

## Translations


When making changes to text (e.g. GraphML files) translations should be updated. 
To update translations run this command from within the docker container:

     ./manage.py translations update

Using the Transifex account that has been added as a Project maintainer to the `cla_public` project,
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

## Installation in a virtual environment

This is here for completeness and will not be updated but gives instructions for creating a virtual environment
and running django from the console.


Clone the repository:

    git clone git@github.com:ministryofjustice/cla_backend.git

Next, create the environment and start it up:

    cd cla_backend
    virtualenv -p python2.7 env --prompt=\(cla_be\)

    source env/bin/activate

Update pip to the latest version:

    pip install -U pip

Install python dependencies:

    pip install -r requirements/dev.txt

Create the database inside postgres. Make sure the postgres service is started. Type `psql -d template1` to enter postgres, then enter:

    CREATE DATABASE cla_backend WITH ENCODING 'UTF-8';
    \c cla_backend
    create extension pgcrypto;

You should see a message saying `CREATE EXTENSION`. If you get an error instead, if means that you don't have the related lib installed. This is a rare case as `postgresql-contrib` gets installed automatically by homebrew and postgresapp. In linux, you can install it using `sudo apt-get install postgresql-contrib`

Now make postgres create the extension automatically when new databases are created,
this is useful otherwise the test command will error.

Open a terminal and type:

    psql -d template1 -c 'create extension pgcrypto;'

For OSX, update the `PATH` and `DYLD_LIBRARY_PATH` environment variables if necessary:

    export PATH="/Applications/Postgres.app/Contents/MacOS/bin/:$PATH"
    export DYLD_LIBRARY_PATH="/Applications/Postgres.app/Contents/MacOS/lib/:$DYLD_LIBRARY_PATH"

Create a `local.py` settings file from the example file:

    cp cla_backend/settings/.example.local.py cla_backend/settings/local.py

Sync and migrate the database (n.b. see [Troubleshooting](#troubleshooting) if the `postgres` role is missing):

    ./manage.py migrate

Create an admin user by running the following command and specifying username == password == 'admin' (email choice not relevant):

    ./manage.py createsuperuser

Load initial data:

    ./manage.py loaddata initial_groups.json kb_from_knowledgebase.json initial_category.json test_provider.json test_provider_allocations.json initial_mattertype.json test_auth_clients.json initial_media_codes.json test_rotas.json initial_guidance_notes.json

Start the server:

    ./manage.py runserver 8000

See [Troubleshooting](#troubleshooting) if this fails because the DEBUG environment variable was not set:

See the list of users in `/admin/auth/user/`. Passwords are the same as the usernames.


