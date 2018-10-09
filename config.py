#!/usr/bin/python3
# # -*- coding:utf-8 -*-
# # Author: daning
import os

user = os.environ.get('mysqlusername') or 'root'
passwd = os.environ.get('mysqlpasswd') or 'passwd'
SECRET_KEY = 'haskha214kNk**#Yilnf#$%*!&'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@127.0.0.1:3306/dbname'.format(user, passwd)
SQLALCHEMY_TRACK_MODIFICATIONS = False
