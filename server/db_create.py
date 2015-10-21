from server.app.extensions import db
from server.app.models import *
from server.app.main import app

db.drop_all(app=app)
db.create_all(app=app)