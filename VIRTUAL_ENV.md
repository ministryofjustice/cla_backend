# Installation in a virtual environment

| :warning: WARNING                                                    |
|:---------------------------------------------------------------------|
| This is not maintained. Use the method in the README.md instead      |

## Pre-requisites

### Pyenv, python2

"pyenv" is used to provide python2. (Recent MacOS versions no longer include python2, and Homebrew no longer provides it.)

1. Install pyenv with brew:

        brew install pyenv

2. Set up your shell for pyenv. Make the changes to `~/.zshrc` described here: [Set up your shell for pyenv](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv) (This is so that pyenv's python binary can be found in your path)

3. To make the shell changes take effect:

        exec "$SHELL"

    (or alternatively, restart your shell)

4. Install into pyenv the python version this repo uses (which is defined in `.python-version`):

    pyenv install 2.7.18 --skip-existing

## Install

Clone the repository:
```
git clone git@github.com:ministryofjustice/cla_backend.git
```

Ensure you have the right Python version on the path:
```
cd cla_frontend
python --version
```
Ensure it reports `Python 2.7.18`. (This should match the version `.python-version`. If it's not correct, check your pyenv shell setup.)

Update 'pip' and install 'virtualenv' (in pyenv's python 2.7.18 environment):
```
pip install -U pip
pip install virtualenv
```

Create the python environment:
```
virtualenv -p python2.7 env --prompt=cla_be
```

Activate the python environment - Linux and Mac:
```
source env/bin/activate
```
or on Windows:
```
env\scripts\activate
```

Install python dependencies:
```
pip install -r requirements/generated/requirements-dev.txt
```

If you get an error with cython building `pyyaml`, then you need to fix cython to <3.0:
```
echo 'Cython < 3.0' > /tmp/constraint.txt
PIP_CONSTRAINT=/tmp/constraint.txt pip install 'PyYAML==5.4'
pip install -r requirements/generated/requirements-dev.txt
```

If you get an error building cryptography then it's likely you need openssl, rust, and some magic:
```
# ERROR: Could not build wheels for cryptography which use PEP 517 and cannot be installed directly
brew install openssl@3 rust
env CRYPTOGRAPHY_SUPPRESS_LINK_FLAGS=1 LDFLAGS="$(brew --prefix openssl@1.1)/lib/libssl.a $(brew --prefix openssl@1.1)/lib/libcrypto.a" CFLAGS="-I$(brew --prefix openssl@1.1)/include" pip install cryptography==3.3.2
pip install -r requirements/generated/requirements-dev.txt
```

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

    DEBUG=True ./manage.py runserver 0.0.0.0:8000

See the list of users in `/admin/auth/user/`. Passwords are the same as the usernames.
