## Installation in a virtual environment

NB Old Macbooks no longer have python 2.7 installed. 
If you want to install a 2.7 virtualenv then use pyenv-virtualenv
https://github.com/pyenv/pyenv-virtualenv

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

