# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
# pylint: disable=no-name-in-module,import-error
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user, logout_user
from flask_table import Col, Table
from sqlalchemy import Numeric

from tegenaria_web.extensions import login_manager
from tegenaria_web.models import Apartment
from tegenaria_web.public.forms import LoginForm
from tegenaria_web.user.forms import RegisterForm
from tegenaria_web.user.models import User
from tegenaria_web.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder="../static")  # pylint: disable=invalid-name


@login_manager.user_loader
def load_user(id):  # pylint: disable=redefined-builtin
    """Load user by ID."""
    return User.get_by_id(int(id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout page."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    """Register user page."""
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data,
                    password=form.password.data, active=True)
        flash("Thank you for registering. You can now log in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)


@blueprint.route("/apartments/")
def apartments():
    """List all apartments."""
    class ApartmentTable(Table):

        """An HTML table for the apartments."""

        title = Col('Title')
        url = Col('URL')
        address = Col('Address')
        neighborhood = Col('Neighborhood')
        warm_rent = Col('Warm Rent')
        warm_rent_notes = Col('Notes')
        cold_rent = Col('Cold Rent')

        def sort_url(self, col_id, reverse=False):
            """Sort the table by clicking its headers."""
            pass

    # pylint: disable=no-member
    items = Apartment.query.order_by(
        Apartment.warm_rent.cast(Numeric),
        Apartment.cold_rent.cast(Numeric)).all()
    table = ApartmentTable(items, classes=['table-bordered', 'table-striped'])
    return render_template("public/apartments.html", table=table)