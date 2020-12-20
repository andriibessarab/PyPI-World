from flask import Blueprint, request, session, render_template
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import json
import re

from models import User, Package
from extensions import db
from functions import validate_form, form_validation_results_json
from variables import inputs_info


main = Blueprint(
    "main",
    __name__
)


@main.route("/", methods=["GET"])
def index__route():
    if current_user.is_authenticated:
        # Query all user's user_packages
        user_pkgs = Package.query.filter_by(user_id=current_user.id).all()

        return render_template("homepage.html", user_pkgs=user_pkgs)
    else:
        return render_template("index.html")


@main.route("/account", methods=["GET", "POST"])
@login_required
def account__route():
    if request.method == "POST":
        try:
            # Request form
            form = request.form
            inputs_errors = {}


            # Check if all inputs are valid
            validation_results = validate_form(
                form=form,
                form_inputs=["email", "pypi_token", "github_username", "github_token"],
                form_required_inputs=["email", "pypi_token", "github_username", "github_token"]
            )
            if not validation_results["valid"]:
                return form_validation_results_json(
                    form_error="Some input(s) don't match the pattern",
                    inputs_errors=validation_results["inputs-errors"]
                )


            # Check if email and tokens are available
            if User.query.filter(User.id != current_user.id, User.email == form["email"]).all():
                inputs_errors["email"] = "Email used by another user"
            if User.query.filter(User.id != current_user.id, User.pypi_token == form["pypi_token"]).all():
                inputs_errors["pypi_token"] = "Token used by another user"
            if User.query.filter(User.id != current_user.id, User.github_token == form["github_token"]).all():
                inputs_errors["pypi_token"] = "Token used by another user"
            if inputs_errors:
                return form_validation_results_json(
                    form_error="Some of the information you provided is used by another account(s)",
                    inputs_errors=inputs_errors
                )


            # Query current user
            user = User.query.filter_by(username=current_user.username).first()


            # Change information about user in database
            user.email = form["email"]
            user.pypi_token = form["pypi_token"]
            user.github_username = form["github_username"]
            user.github_token = form["github_token"]
            db.session.commit()


            # Return positive response
            return form_validation_results_json(success=True)
        except:
            return form_validation_results_json(unexpected_error=True)
    elif request.method == "GET":
        return render_template("account_page.html")


@main.route("/start", methods=["GET", "POST"])
@login_required
def start__route():
    if request.method == "POST":
        try:
            if current_user.pypi_token or not current_user.github_token:
                # Request form data
                form = request.form
                inputs_errors = {}

                # Check if all inputs are valid
                validation_results = validate_form(
                    form=form,
                    form_inputs=["pkg_name"],
                    form_required_inputs=["pkg_name"]
                )
                if not validation_results["valid"]:
                    return form_validation_results_json(
                        form_error="Some input(s) don't match the pattern",
                        inputs_errors=validation_results["inputs-errors"]
                    )

                # Check if pkg with same name exists
                if Package.query.filter_by(user_id=current_user.id, pkg_name=form["pkg_name"]).first():
                    inputs_errors["pkg_name"] = "Name is taken"
                    return form_validation_results_json(
                        form_error="Package with the same name already exists",
                        inputs_errors=inputs_errors
                    )

                # Define & add pkg to database
                new_pkg = Package(user_id=current_user.id, pkg_name=form["pkg_name"])
                db.session.add(new_pkg)
                db.session.commit()

                # Return positive response
                return form_validation_results_json(success=True)
            else:
                return form_validation_results_json(unexpected_error=True)
        except:
            return json.dumps(
                {
                    "success": False,
                    "unexpected-error": True,
                    "form-errors": {
                        "error": None,
                        "inputs": None
                    }
                }
            )
    elif request.method == "GET":
        return render_template("start_new_package.html")
