#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: daning

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Images(db.Model):
    image_data = db.Column(db.BLOB)
    image_name = db.Column(db.VARCHAR(255))
    image_copyright = db.Column(db.VARCHAR(255))
    image_urlbase = db.Column(db.VARCHAR(255), primary_key=True)
    image_date = db.Column(db.VARCHAR(255), index=True)
    image_position = db.Column(db.VARCHAR(255))
    image_description = db.Column(db.VARCHAR(255))

    def get(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return f'<Images {self.image_date} {self.image_copyright}>'
