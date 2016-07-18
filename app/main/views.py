# -*- coding: utf-8 -*-
from . import main
from flask import render_template, session, url_for, redirect
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(Form):
    name = StringField('what is you name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        return redirect(url_for('Blueprint.index'))
    return render_template('index.html', form=form, name=session.get('name'))