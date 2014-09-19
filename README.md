# CLA backend

Backend API for the Civil Legal Aid Tool.

## Dependencies

* [Virtualenv](http://www.virtualenv.org/en/latest/)
* [Python](http://www.python.org/) (Can be installed using `brew`)
* [Postgres](http://www.postgresql.org/)

## Installation

Clone the repository:

    git clone git@github.com:ministryofjustice/cla_backend.git

Next, create the environment and start it up:

    virtualenv env --prompt=\(cla_be\)

    source env/bin/activate

Install python dependencies:

    pip install -r requirements/local.txt

Create the database inside postgres. Type `psql` to enter postgres, then enter:

    CREATE DATABASE cla_backend WITH ENCODING 'UTF-8';

For OSX update the `PATH` and `DYLD_LIBRARY_PATH` environment variables:

    export PATH="/Applications/Postgres.app/Contents/MacOS/bin/:$PATH"
    export DYLD_LIBRARY_PATH="/Applications/Postgres.app/Contents/MacOS/lib/:$DYLD_LIBRARY_PATH"

Sync and migrate the database: When prompted to create an Admin user, accept all defauls and use password 'admin'.

    ./manage.py syncdb
    ./manage.py migrate

Load initial data:

    ./manage.py loaddata kb_from_spreadsheet.json initial_category.json test_provider.json initial_mattertype.json test_auth_clients.json initial_media_codes.json test_rotas.json

Start the server:

    ./manage.py runserver 8000

See the list of users in `/admin/auth/user/`. Passwords are the same as the usernames.

## Dev

Each time you start a new terminal instance you will need to run the following commands to get the server running again:

    source env/bin/activate

    ./manage.py runserver 8000


## Troubleshooting

If you are experiencing errors when creating and sycning the database, make sure the following are added to your `PATH` var (amend path to postgres as necessary):

    export PATH="/Applications/Postgres.app/Contents/MacOS/bin/:$PATH"
    export DYLD_LIBRARY_PATH=/Applications/Postgres.app/Contents/MacOS/lib/
