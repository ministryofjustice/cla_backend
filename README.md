# CLA Backend

[![CircleCI](https://circleci.com/gh/ministryofjustice/cla_backend/tree/master.svg?style=svg)](https://circleci.com/gh/ministryofjustice/cla_backend/tree/master)
[![Coverage Status](https://coveralls.io/repos/github/ministryofjustice/cla_backend/badge.svg?branch=master)](https://coveralls.io/github/ministryofjustice/cla_backend?branch=master)
    
Backend API, part of the Civil Legal Advice product. It is used by cla_public and cla_frontend.

It is the **data layer** for the product, containing:

* cases - personal and financial details of a person wanting civil legal advice, built-up during application (cla_public), and updated by call centre operators and a specialist provider (cla_frontend)

* users - call centre operators and specialist providers, with their sign-in credentials, organisation

* call centre case management - for staff rotas, to assign cases to providers etc

* reference data on the legal categories ('category of law' & 'matter type') and whether legal aid is available to provide Civil Legal Advice

It has **business logic**, shared across cla_public and cla_frontend:

* auth - providing OAuth2 and authorization (`cla_auth`)
* means test (`EligibilityChecker`)

It also has a bit of **presentation layer**, shared across cla_public and cla_frontend:

* sign in - results in an access_token provided to cla_public or cla_frontend


## Installation for development

For development of CLA Backend, we use Docker Compose to run the 'development' main app container 'cla_backend' and its supporting containers: database, celery worker, rabbitmq.

Clone the repository:

    git clone git@github.com:ministryofjustice/cla_backend.git
    cd cla_backend

To start the containers:

    ./run_local.sh

You can connect to the fox admin application from http://localhost:8010/admin and log in as cla_admin

The run_local.sh script is reliable but slow. Usually you can quickly restart containers with just:

    docker-compose run start_applications

### Troubleshooting

If you get `initdb: could not create directory "/var/lib/postgresql/data/pg_wal": No space left on device` when running the containers, then it's a problem with disk space in the linux virtual machine that Docker Desktop runs containers in. You probably have old Docker images hanging around. To clear space:

    docker system prune

### Tips for developing with docker containers

Code editing - You can edit the code on your local disk, with a local editor, as normal. (You don't have to edit the files inside the Docker container, because your local directory is mounted into container.) When you save a file, it becomes present in the container immediately, and the server restarts.

Browsing the app - Point your local browser at http://localhost:8010/admin/ and log in as cla_admin. This works because Docker connects your local port 8010 to port 8000 in the container.

Log output - watch the output generated by the running app using: `docker logs cla_backend -f` or `docker attach cla_backend`

It's suggested to have two terminals open:

1. Run containers and 'exec' into a shell in the app container

        docker-compose run start_applications && docker exec -it cla_backend bash

    or occasionally it won't run without first doing:

        ./run_local.sh

    From the shell inside the container you can run some tests e.g.

        python manage.py test --settings=cla_backend.settings.circle cla_backend.libs.eligibility_calculator.tests.test_calculator.DoCfeCivilCheckTestCase

2. Logs and debugging

    You can see the logging output by attaching to the container:

        docker attach cla_backend

    If you added pdb breakpoints, this is where you can interact with this debugger.

Alternatively, some editors have functionality to hook into running containers, such as VS Code's 'Dev Containers' extension.

## Debugging

Ensure your container is running Once you have created your docker development container as above. 

Add `import pdb; pdb.set_trace()` as a 'breakpoint' line in the code, where you want to trigger the debugger.

Now run `docker attach cla_backend` to view the output

When pdb.set_trace() is reached, you will be able to debug from the command line.

`https://docs.python.org/3/library/pdb.html`

## Unit/integration tests

If you wish to limit the tests that are run you should exec into the container and run them locally

    docker exec -it cla_backend bash

Once you are in the development container, set the correct settings file for report tests to run and then choose your test, eg:

    python manage.py test --settings=cla_backend.settings.circle cla_backend.apps.legalaid.tests.test_views.FullCaseViewSetTestCase

For example of running a test class's tests:
    `cla_backend.apps.legalaid.tests.test_views.FullCaseViewSetTestCase`

Or to run one test:
    `cla_backend.apps.legalaid.tests.test_views.FullCaseViewSetTestCase.test_search_unicode`

To run all tests, this could be done from within the development container (as above), or you can run the test environment:

    ./run_local.sh test

## Lint and pre-commit hooks

To lint with Black and flake8, install pre-commit hooks:

```
virtualenv -p python2.7 env --prompt=\(cla_be\)
. env/bin/activate
 pip install -r requirements/generated/requirements-lint.txt
pre-commit install
```

To run them manually:
```
pre-commit run --all-files
```

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

## run_local.sh

run_local.sh is a wrapper for running the Docker containers for 3 different purposes on your local machine.

There is one Dockerfile, but it contains options to create 3 variants of the Docker container, for different purposes. run_local.sh is our script to build and run the different container variants, and also run supporting containers, orchestrated with Docker Compose.

### development container

The 'development container' has the requirements-dev installed. It serves the app with Django's built-in runserver.

To start the development container (with supporting containers):
```
./run_local.sh
```

### test container

The 'test container' has requirements-dev installed. On start, it runs the unit/integration tests, with minimal log output.

To run the tests:
```
./run_local.sh test
```

### production container

The 'production container' is what gets run in the production environment. It serves the app with uwsgi.

To run the production container:
```
./run_local.sh production
```

## Translations

| :warning: WARNING                                   |
|:----------------------------------------------------|
| This is not usually required and/or maintained      |

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

| :warning: WARNING                                   |
|:----------------------------------------------------|
| This is not usually required and/or maintained      |

* Edit the .graphml files, e.g. using a tool like [yEd](http://www.yworks.com/en/products/yfiles/yed/), to change the scope diagnosis trees
* Run Django management command `python manage.py translations update` to update translations and templated graph files

See more detailed instructions in the [how-to guide](https://dsdmoj.atlassian.net/wiki/spaces/laagetaccess/pages/1005060261/Produce+diagram+of+CLA+merits+decision+tree) on Confluence (log-in required).

## Installation in a virtual environment

| :warning: WARNING                                   |
|:----------------------------------------------------|
| This is not usually required and/or maintained      |

This is here for completeness and will not be updated but gives instructions for creating a virtual environment
and running django from the console.

[Installation in a virtual environment](VIRTUAL_ENV.md)
