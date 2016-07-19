# -*- coding: utf-8 -*-
from . import main
from flask import render_template, session, url_for, redirect, abort, flash
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from ..models import User
from flask_login import login_required, current_user
from forms import EditProfileForm
from .. import db

class NameForm(Form):
    name = StringField('what is you name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        return redirect(url_for('main.index'))
    return render_template('index.html', form=form, name=session.get('name'))


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


# 修改用户资料
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('You profile has been updated')
        return redirect(url_for('.user', username=current_user.usernaem))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)