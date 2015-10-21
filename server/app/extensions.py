# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api


# flask-sqlalchemy
db = SQLAlchemy()

# flask-bcrypt
bcrypt = Bcrypt()

# flask-httpauth
auth = HTTPBasicAuth()



