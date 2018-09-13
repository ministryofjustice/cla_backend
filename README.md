# CLA Backend


[![CircleCI](https://circleci.com/gh/ministryofjustice/cla_backend/tree/develop.svg?style=svg)](https://circleci.com/gh/ministryofjustice/cla_backend/tree/develop)
    
Backend API for the Civil Legal Aid Tool.

## Dependencies

-  [Virtualenv](http://www.virtualenv.org/en/latest/)
-  Most recent version of pip
-  [Python 2.7](http://www.python.org/) Can be installed using `brew`)
-  [Postgres 9.3+](http://www.postgresql.org/)

## Installation

Clone the repository:

    git clone git@github.com:ministryofjustice/cla_backend.git

Next, create the environment and start it up:

    cd cla_backend
    virtualenv env --prompt=\(cla_be\)

    source env/bin/activate

Update pip to the latest version:

    pip install -U pip

Install python dependencies:

    pip install -r requirements/local.txt

Create the database inside postgres. Type `psql -d template1` to enter postgres, then enter:

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

Sync and migrate the database:

    ./manage.py migrate

Create an admin user by running the following command and specifying username == password == 'admin':

    ./manage.py createsuperuser

Load initial data:

    ./manage.py loaddata initial_groups.json kb_from_knowledgebase.json initial_category.json test_provider.json test_provider_allocations.json initial_mattertype.json test_auth_clients.json initial_media_codes.json test_rotas.json

Start the server:

    ./manage.py runserver 8000

See the list of users in `/admin/auth/user/`. Passwords are the same as the usernames.

## Dev

Each time you start a new terminal instance you will need to run the following commands to get the server running again:

    source env/bin/activate
    ./manage.py runserver 8000

## Translations

When making changes to text (e.g. GraphML files) translations should be updated. To update translations run:

     ./manage.py translations update


## Scope Graphs

* Edit the .graphml files, e.g. using a tool like [yEd](http://www.yworks.com/en/products/yfiles/yed/), to change the scope diagnosis trees
* Run Django management command `python manage.py translations update` to update translations and templated graph files

See more detailed instructions in the [how-to guide](https://dsdmoj.atlassian.net/wiki/spaces/laagetaccess/pages/1005060261/Produce+diagram+of+CLA+merits+decision+tree) on Confluence (log-in required).


## Troubleshooting

If you are experiencing errors when creating and syncing the database, make sure the following are added to your `PATH` var (amend path to postgres as necessary):

    export PATH="/Applications/Postgres.app/Contents/Versions/9.3/bin/:$PATH"
    export DYLD_LIBRARY_PATH="/Applications/Postgres.app/Contents/Versions/9.3/lib/:$DYLD_LIBRARY_PATH"

If you get the error `django.db.utils.OperationalError: FATAL:  role "postgres" does not exist`, you will need to create the user `postgres` on the database.

    createuser -s -e postgres

## Releasing

### Releasing to non-production

1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/cla_backend) for the feature branch.
1. Copy the `feature_branch.<sha>` reference from the `build` job's "Push Docker image" step. Eg:
    ```
    Pushing tag for rev [9a77ce2f0e8a] on {https://registry.service.dsd.io/v1/repositories/cla_backend/tags/dual-docker-registries.902c45d}
    ```
1. [Deploy `feature_branch.<sha>`](https://ci.service.dsd.io/job/DEPLOY-cla_backend/build?delay=0sec).
    * `APP_BUILD_TAG` is the branch that needs to be released plus a specific 7-character prefix of the Git SHA. (`dual-docker-registries.902c45d` for the above example).
    * `environment` is the target environment, select depending on your needs, eg. "demo", "staging", etc.
    * `deploy_repo_branch` is the [deploy repo's](https://github.com/ministryofjustice/cla_backend-deploy) default branch name, usually master.

### Releasing to production

1. Please make sure you tested on a non-production environment before merging.
1. Merge your feature branch pull request to `master`.
1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/cla_backend/tree/master) for the `master` branch.
1. Copy the `master.<sha>` reference from the `build` job's "Push Docker image" step. Eg:
    ```
    Pushing tag for rev [d96e0157bdac] on {https://registry.service.dsd.io/v1/repositories/cla_backend/tags/master.b24490d}
    ```
1. [Deploy `master.<sha>` to **prod**uction](https://ci.service.dsd.io/job/DEPLOY-cla_backend/build?delay=0sec).

:tada: :shipit:
