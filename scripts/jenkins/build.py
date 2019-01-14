#!/usr/bin/env python
import argparse
import os
import signal
import subprocess
import sys
from Queue import Queue

# use python scripts/jenkins/build.py integration
PROJECT_NAME = "cla_backend"

background_processes = Queue()


def run(command, background=False, **kwargs):
    if "shell" not in kwargs:
        kwargs["shell"] = True

    print("Running {command}".format(command=command))

    if background:
        process = subprocess.Popen(command, **kwargs)
        background_processes.put(process)
        return process

    return_code = subprocess.call(command, **kwargs)
    if return_code:
        sys.exit(return_code)


def kill_child_processes(pid, sig=signal.SIGTERM):
    ps_cmd = subprocess.Popen("ps -o pid --ppid {0} --noheaders".format(pid), shell=True, stdout=subprocess.PIPE)
    ps_out = ps_cmd.stdout.read()
    ps_cmd.wait()
    for pid_str in ps_out.split("\n")[:-1]:
        os.kill(int(pid_str), sig)


def kill_all_background_processes():
    while not background_processes.empty():
        process = background_processes.get()
        try:
            kill_child_processes(process.pid)
            process.kill()
        except OSError:
            pass


def main():
    # args
    parser = argparse.ArgumentParser(description="Build project ready for testing by Jenkins.")
    parser.add_argument("envname", help="e.g. integration, production, etc.")
    parser.add_argument("--skip-tests", action="store_true", help="do not run Django unit tests")
    args = parser.parse_args()

    env = args.envname
    env_name = "%s-%s" % (PROJECT_NAME, env)
    env_path = "/tmp/jenkins/envs/%s" % env_name
    bin_path = "%s/bin" % env_path

    # setting up virtualenv
    if not os.path.isdir(env_path):
        run("virtualenv %s" % env_path)

    run("%s/pip install -U setuptools pip wheel" % bin_path)
    run("%s/pip install -r requirements/jenkins.txt" % bin_path)

    # Remove .pyc files from the project
    run("find . -name '*.pyc' -delete")

    if not args.skip_tests:
        print("Starting tests...")

        run(
            "%s/python manage.py jenkins "
            "--coverage-rcfile=.coveragerc "
            "--settings=cla_backend.settings.jenkins" % bin_path
        )


if __name__ == "__main__":
    try:
        main()
    finally:
        kill_all_background_processes()
