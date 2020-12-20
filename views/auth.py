from flask import Blueprint, request, session, render_template, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import re

from models import User, Package
from extensions import db
from functions import logout_required, validate_form, form_validation_results_json
from variables import inputs_info


auth = Blueprint(
    "auth",
    __name__
)


@auth.route("/auth", methods=["GET"])
@logout_required
def auth__route():
    return render_template("auth.html")


@auth.route("/auth/register", methods=["POST"])
@logout_required
def auth_register__route():
    try:
        # Request form
        form = request.form
        inputs_errors = {}


        # Check if all inputs are valid
        validation_results = validate_form(
            form=form,
            form_inputs=["fullname", "username", "email", "password"],
            form_required_inputs=["fullname", "username", "email", "password"]
        )
        if not validation_results["valid"]:
            return form_validation_results_json(
                form_error="Some input(s) don't match the pattern",
                inputs_errors=validation_results["inputs-errors"]
            )


        # Check if username and email are available
        if bool(User.query.filter_by(username=form["username"]).first()):
            inputs_errors["username"] = "Username is taken"
        if bool(User.query.filter_by(email=form["email"]).first()):
            inputs_errors["email"] = "Email is taken"
        if inputs_errors:
            return form_validation_results_json(
                form_error="Username or/and email are taken",
                inputs_errors=inputs_errors
            )


        # Add user to database
        user = User(fullname=form["fullname"], username=form["username"], email=form["email"],
                        password=generate_password_hash(form["password"]))
        db.session.add(user)
        db.session.commit()

        # Log user in
        login_user(user)

        return form_validation_results_json(success=True)
    except:
        return form_validation_results_json(unexpected_error=True)


@auth.route("/auth/login", methods=["POST"])
@logout_required
def auth_login__route():
    try:
        # Request form data
        form = request.form
        inputs_errors = {}


        # Check if all inputs are valid
        validation_results = validate_form(
            form=form,
            form_inputs=["username", "password"],
            form_required_inputs=["username", "password"]
        )
        if not validation_results["valid"]:
            return form_validation_results_json(
                form_error="Invalid user",
                inputs_errors=validation_results["inputs-errors"]
            )


        # Query user
        user = User.query.filter_by(username=form["username"]).first()


        # If user exists, log him in
        if user and check_password_hash(user.password, form["password"]):
            login_user(user)
        else:
            inputs_errors["username"] = "Incorrect username or password"

            return form_validation_results_json(
                form_error="User doesn't exist",
                inputs_errors=inputs_errors
            )


        return form_validation_results_json(success=True)
    except:
        return form_validation_results_json(unexpected_error=True)


@auth.route("/auth/logout", methods=["GET"])
@login_required
def auth_logout__route():
    try:
        # Remove user from session
        logout_user()

        # Redirect user to homepage
        return redirect(url_for("main.index__route"))
    except:
        return render_template("error.html", error="Couldn't log you out. Please try again!")
