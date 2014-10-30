CLA Backend
###########

Backend API for the Civil Legal Aid Tool.

Dependencies
------------

-  `Virtualenv <http://www.virtualenv.org/en/latest/>`__
-  `Python 2.7 <http://www.python.org/>`__ (Can be installed using ``brew``)
-  `Postgres 9.3+ <http://www.postgresql.org/>`__

Installation
------------

Clone the repository:

::

    git clone git@github.com:ministryofjustice/cla_backend.git

Next, create the environment and start it up:

::

    cd cla_backend
    virtualenv env --prompt=\(cla_be\)

    source env/bin/activate

Install python dependencies:

::

    pip install -r requirements/local.txt

Create the database inside postgres. Type ``psql`` to enter postgres,
then enter:

::

    CREATE DATABASE cla_backend WITH ENCODING 'UTF-8';
    \c cla_backend
    create extension pgcrypto;

You should see a message saying ``CREATE EXTENSION``. If you get an error instead, if means that
you don't have the related lib installed. This is a rare case as ``postgresql-contrib``
gets installed automatically by homebrew and postgresapp.
In linux, you can install it using ``sudo apt-get install postgresql-contrib``

Now make postgres create the extension automatically when new databases are created,
this is useful otherwise the test command will error.

Open a terminal and type:

::

    psql -d template1 -c 'create extension pgcrypto;'


For OSX, update the ``PATH`` and ``DYLD_LIBRARY_PATH`` environment
variables if necessary:

::

    export PATH="/Applications/Postgres.app/Contents/MacOS/bin/:$PATH"
    export DYLD_LIBRARY_PATH="/Applications/Postgres.app/Contents/MacOS/lib/:$DYLD_LIBRARY_PATH"

Create a ``local.py`` settings file from the example file:

::

    cp cla_backend/settings/.example.local.py cla_backend/settings/local.py

Sync and migrate the database: When prompted to create an Admin user,
accept all defaults and use password 'admin'.

::

    ./manage.py syncdb
    ./manage.py migrate

Load initial data:

::

    ./manage.py loaddata kb_from_spreadsheet.json initial_category.json test_provider.json initial_mattertype.json test_auth_clients.json initial_media_codes.json test_rotas.json

Start the server:

::

    ./manage.py runserver 8000

See the list of users in ``/admin/auth/user/``. Passwords are the same
as the usernames.

Dev
---

Each time you start a new terminal instance you will need to run the
following commands to get the server running again:

::

    source env/bin/activate

    ./manage.py runserver 8000

Troubleshooting
---------------

If you are experiencing errors when creating and sycning the database,
make sure the following are added to your ``PATH`` var (amend path to
postgres as necessary):

::

    export PATH="/Applications/Postgres.app/Contents/MacOS/bin/:$PATH"
    export DYLD_LIBRARY_PATH=/Applications/Postgres.app/Contents/MacOS/lib/



