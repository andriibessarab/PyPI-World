from flask import Blueprint, request, session, render_template, redirect, url_for
from flask_login import login_required, current_user
import json
import re

from models import User, Package, Setup
from extensions import db
from functions import logout_required, is_package_of_current_user, validate_form, publish_pkg, form_validation_results_json, publication_results_json
from variables import setup_args_info, inputs_info


pkg = Blueprint(
    "pkg",
    __name__
)


@pkg.route("/pkg", methods=["GET"])
@login_required
def user_packages__route():
    try:
        # Query all user's packages
        user_pkgs = Package.query.filter_by(user_id=current_user.id).all()
        user_setups = {}

        for pkg in user_pkgs:
            setup = Setup.query.filter_by(id=pkg.setup_id).first()
            if setup:
                user_setups[pkg.id] = setup

        return render_template("user_packages.html", user_pkgs=user_pkgs, user_setups=user_setups)

    except:
        return render_template("error.html", error="Unexpected Error Occured! Please Try Again.")


@pkg.route("/pkg/<pkg_name>", methods=["GET"])
@login_required
def pkg_page__route(pkg_name):
    try:
        # Query package
        pkg = Package.query.filter_by(user_id=current_user.id, pkg_name=pkg_name).first()

        # Check if package exists
        if not pkg:
            return render_template("error.html", error="Package doesn't exist")

        # Query setup
        setup = Setup.query.filter_by(id=pkg.setup_id).first()

        return render_template("package_page.html", pkg=pkg, setup=setup)
    except:
        return render_template("error.html", error="Unexpected error occured. Please try again!")


@pkg.route("/pkg/<pkg_name>/connect_github", methods=["POST"])
@login_required
def pkg_connect_github__route(pkg_name):

    try:
        # Query package
        pkg = Package.query.filter_by(user_id=current_user.id, pkg_name=pkg_name).first()

        # Request form
        form = request.form
        inputs_errors = {}

        # Check if all inputs are valid
        validation_results = validate_form(
            form=form,
            form_inputs=["github_repo_name"],
            form_required_inputs=["github_repo_name"]
        )
        if not validation_results["valid"]:
            return form_validation_results_json(
                form_error="Some input(s) don't match the pattern",
                inputs_errors=validation_results["inputs-errors"]
            )

        # Check if this repo hasn't been used for another packages
        if Package.query.filter(Package.user_id==current_user.id, Package.pkg_name!=pkg_name, Package.github_repo_name==form["github_repo_name"]).all():
            inputs_errors["github_repo_name"] = "Already used"
            return form_validation_results_json(
                form_error="This GitHub Repo already connected to another package",
                inputs_errors=inputs_errors
            )

        # Add github_repo_url to database
        pkg.github_repo_name = form["github_repo_name"]
        db.session.commit()

        return form_validation_results_json(success=True)

    except:
        return form_validation_results_json(unexpected_error=True)


@pkg.route("/pkg/<pkg_name>/generate_setup", methods=["POST"])
@login_required
def pkg_generate_setup__route(pkg_name):
    try:
        # Query package & setup
        pkg = Package.query.filter_by(user_id=current_user.id, pkg_name=pkg_name).first()
        setup = Setup.query.filter_by(id=pkg.setup_id).first()

        # Check if package belong to user
        if not pkg.github_repo_name:
            return form_validation_results_json(form_error="You can't perform this action. Connect GitHub Repository first.")

        # Declare variables
        form = request.form
        inputs_errors = {}
        setup_args = []
        setup_required_args = []
        for i in setup_args_info:
            arg_name = "setup_" + i["name"]
            setup_args.append(arg_name)
            if i["required"] and not (arg_name == "setup_name" and pkg.is_published):
                setup_required_args.append(arg_name)


        # Check if all inputs are valid
        validation_results = validate_form(
            form=form,
            form_inputs=setup_args,
            form_required_inputs=setup_required_args
        )
        if not validation_results["valid"]:
            return form_validation_results_json(
                form_error="Some input(s) don't match the pattern",
                inputs_errors=validation_results["inputs-errors"]
            )

        # Add setup to database
        if setup:
            if not pkg.is_published:
                setup.name=form["setup_name"]
            setup.version=form["setup_version"]
            setup.description=form["setup_description"]
            setup.long_description=form["setup_long_description"]
            setup.keywords=form["setup_keywords"]
            setup.python_version=form["setup_python_version"]
        else:
            setup = Setup(
                name=form["setup_name"],
                version=form["setup_version"],
                description=form["setup_description"],
                long_description=form["setup_long_description"],
                author=current_user.fullname,
                author_email=current_user.email,
                keywords=form["setup_keywords"],
                python_version=form["setup_python_version"]
            )
            db.session.add(setup)
            db.session.commit()
            pkg.setup_id = setup.id
        db.session.commit()

        return form_validation_results_json(success=True)

    except:
        return form_validation_results_json(unexpected_error=True)


@pkg.route("/pkg/<pkg_name>/publish", methods=["POST"])
@login_required
def pkg_publish__route(pkg_name):
    try:
        # Query package
        pkg = Package.query.filter_by(user_id=current_user.id, pkg_name=pkg_name).first()
        setup = Setup.query.filter_by(id=pkg.setup_id).first()

        # Check if package belong to user
        if not pkg.github_repo_name or not setup:
            return json.dumps(publication_results_json(error="You can't perform this action"))

        # Publish pkg
        publication_results = publish_pkg(pkg)

        # Mark package as published if published successfully
        if publication_results["successful-publication"]:
            pkg.is_published = True
            pkg.updated_on = db.func.now()
            db.session.commit()

        return json.dumps(publication_results)

    except:
        return json.dumps(
            {
                "unexpected-error": True,
            }
        )


@pkg.route("/pkg/<pkg_name>/delete", methods=["GET", "POST"])
@login_required
def delete_pkg__route(pkg_name):
    try:
        # Query package & setup from the database
        pkg = Package.query.filter_by(user_id=current_user.id, pkg_name=pkg_name).first()

        if not pkg:
            return render_template("error.html", error="Package doesn't exist!")

        if pkg.is_published:
            return redirect(url_for("pkg.pkg_page__route", pkg_name=pkg.pkg_name))

        # Query setup
        setup = Setup.query.filter_by(id=pkg.setup_id).first()

        if request.method == "POST":

            # Remove pkg & setup from database
            db.session.delete(pkg)
            db.session.delete(setup)
            db.session.commit()

            return redirect(url_for("pkg.user_packages__route", pkg_name=pkg_name))

        elif request.method == "GET":
            return render_template("delete_package.html", pkg=pkg)

    except:
        return render_template("error.html", error="Unexpected Error Occured! Try Again.")
