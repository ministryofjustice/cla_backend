CLA Backend
###########

.. image:: https://circleci.com/gh/ministryofjustice/cla_backend.svg?style=svg
    :target: https://circleci.com/gh/ministryofjustice/cla_backend
    
Backend API for the Civil Legal Aid Tool.

Dependencies
------------

-  `Virtualenv <http://www.virtualenv.org/en/latest/>`__
-  `Most recent version of pip`
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

Update pip to the latest version:

::

    pip install -U pip

Install python dependencies:

::

    pip install -r requirements/local.txt

Create the database inside postgres. Type ``psql -d template1`` to enter postgres,
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

Sync and migrate the database:

::

    ./manage.py migrate

Create an admin user by running the following command and specifying username == password == 'admin':

::

    ./manage.py createsuperuser

Load initial data:

::

    ./manage.py loaddata initial_groups.json kb_from_knowledgebase.json initial_category.json test_provider.json test_provider_allocations.json initial_mattertype.json test_auth_clients.json initial_media_codes.json test_rotas.json

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

Translaltions
-------------

When making changes to text (e.g. GraphML files) translations should be updated. To update translations run:

::

     ./manage.py translations update


Scope Graphs
============

* Edit the .graphml files, e.g. using a tool like [yEd](http://www.yworks.com/en/products/yfiles/yed/), to change the scope diagnosis trees
* Run Django management command `python manage.py translations update` to update translations and templated graph files


Troubleshooting
---------------

If you are experiencing errors when creating and syncing the database,
make sure the following are added to your ``PATH`` var (amend path to
postgres as necessary):

::

    export PATH="/Applications/Postgres.app/Contents/Versions/9.3/bin/:$PATH"
    export DYLD_LIBRARY_PATH="/Applications/Postgres.app/Contents/Versions/9.3/lib/:$DYLD_LIBRARY_PATH"

If you get the error `django.db.utils.OperationalError: FATAL:  role "postgres" does not exist`, you will need to create the user `postgres` on the database.


::
    createuser -s -e postgres
