#! /usr/bin/python3
# -*- coding:utf-8 -*-
# Author: daning
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ImageSearch(FlaskForm):
    imagedate = StringField(validators=[DataRequired(), ])
    submit = SubmitField('提交')
