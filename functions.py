from flask import redirect, url_for
from flask_login import current_user
from git import Repo
from pathlib import PosixPath
import functools
import subprocess
import shutil
import json
import re

from extensions import login_manager
from models import User, Package, Setup
from variables import inputs_info


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth.auth__route"))


def logout_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("main.index__route"))
        return f(*args, **kwargs)
    return decorated_function


def validate_form(form, form_inputs, form_required_inputs):

    inputs_errors= {}

    for i in form_inputs:

        # Declare variables
        input = form.get(i)
        input_is_required = i in form_required_inputs

        # Check if input has value
        if not input:
            if input_is_required:
                inputs_errors[i] = " "
            continue

        # Declare variables
        input = str(input)
        input_len = len(input)
        input_re = inputs_info[i]["regex"]
        input_re_note = inputs_info[i]["regex-note"]
        input_min_len = inputs_info[i]["min-length"]
        input_max_len = inputs_info[i]["max-length"]

        # Validate input
        if not re.fullmatch(input_re, input) or input_len < input_min_len or input_len > input_max_len:
            inputs_errors[i] = input_re_note
            continue

    return {
        "valid": not bool(inputs_errors),
        "inputs-errors": inputs_errors,
    }


def form_validation_results_json(success=False, unexpected_error=False, form_error=None, inputs_errors=None):
    return json.dumps(
        {
            "success": success,
            "unexpected-error": unexpected_error,
            "error": {
                "form-error": form_error,
                "inputs-errors": inputs_errors,
            }
        }
    )


def publication_results_json(successful_publication=False, successful_run=False, commands=None, error=None, unexpected_error=False):
    return {
        "successful-publication": successful_publication,
        "successful-run": successful_run,
        "commands": commands,
        "error": error,
        "unexpected-error": unexpected_error,
    }


def is_package_of_current_user(username, pkg_name):
    # Query package from database
    pkg = Package.query.filter_by(user_id=current_user.id, pkg_name=pkg_name).first()

    # Check if package's owner is current user and package exists
    if not username == current_user.username or not pkg:
        return False

    return True


def publish_pkg(pkg):
    # Query user & setup
    user = User.query.filter_by(id=pkg.user_id).first()
    setup = Setup.query.filter_by(id=pkg.setup_id).first()

    # Declare variables
    pkg_settings_dir = str(PosixPath(f"./publish_pkg/{pkg.id}"))
    pkg_content_dir = str(PosixPath(pkg_settings_dir + "/src"))

    try:
        username = user.username
        pkg_name = pkg.pkg_name
        github_username = user.github_username
        github_access_token = user.github_token
        github_repo_name = pkg.github_repo_name
        pypi_token = user.pypi_token
        setup_name = setup.name
        setup_version = setup.version
        setup_description = setup.description
        setup_long_description = setup.long_description.replace("\n", "  \n")
        setup_author = setup.author
        setup_author_email = setup.author_email
        setup_keywords = setup.keywords
        setup_python_version = setup.python_version

        shutil.rmtree(pkg_settings_dir, ignore_errors=True)

        # Clone GitHub Repository
        try:
            Repo.clone_from(f"https://{github_access_token}:@github.com/{github_username}/{github_repo_name}", pkg_content_dir)
        except:
            return publication_results_json(error="Couldn't clone GitHub Repository.")

        # Remove .git directory
        shutil.rmtree(str(PosixPath(pkg_content_dir + "/.git")))

        # Generate __init__.py
        with open(str(PosixPath(pkg_content_dir + "/__init__.py")), "a") as __init__:

            __init__.write("")

        # Generate README.md
        with open(str(PosixPath(pkg_settings_dir + "/README.md")), "w") as readme:

            readme.write(setup_long_description)

        # Generate LICENSE.txt
        with open(str(PosixPath(pkg_settings_dir + "/LICENSE.txt")), "w") as license:

            license.write(f"""Copyright (c) 2020 {setup_author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""")

        # Generate MANIFEST.in
        with open(str(PosixPath(pkg_settings_dir + "/MANIFEST.in")), "w") as manifest:

            manifest.write(f"""include LICENSE.txt""")

        # Generate setup.cfg
        with open(str(PosixPath(pkg_settings_dir + "/setup.cfg")), "w") as setup_cfg:

            setup_cfg.write(f"""[metadata]
license_files = LICENSE.txt""")

        # Generate setup.py
        with open(str(PosixPath(pkg_settings_dir + "/setup.py")), "w") as setup_py:

            setup_py.write(f"""from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='{setup_name}',

    version='{setup_version}',

    {f"description='{setup_description}'," if setup_description else ""}

    long_description=long_description,

    long_description_content_type='text/markdown',

    author='{setup_author}',

    author_email='{setup_author_email}',

    {f"keywords='{setup_keywords}'," if setup_keywords else ""}

    packages=find_packages(),

)""")

        command1 = subprocess.run(["python3", "setup.py", "sdist", "bdist_wheel"], cwd=pkg_settings_dir, capture_output=True)

        command2 = subprocess.run(["twine", "upload", "dist/*", "--username", "__token__", "--password", pypi_token], cwd=pkg_settings_dir, capture_output=True)

        shutil.rmtree(pkg_settings_dir)

        return publication_results_json (
            successful_publication = command1.returncode == 0 and command2.returncode == 0,
            successful_run = True,
            commands = [
                {
                    "command": "python setup.py bdist sdist_wheel",
                    "return-code": command1.returncode,
                    "output": command1.stdout.decode("utf-8"),
                    "error": command1.stderr.decode("utf-8"),
                },
                {
                    "command": "twine upload dist/*",
                    "return-code": command2.returncode,
                    "output": command2.stdout.decode("utf-8"),
                    "error": command2.stderr.decode("utf-8"),
                },
            ],
        )

    except:
        shutil.rmtree(pkg_settings_dir, ignore_errors=True)

        return publication_results_json(unexpected_error=True)
