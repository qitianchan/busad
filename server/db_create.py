from server.app.extensions import db
from server.app.models import *
from server.app.main import create_app
app = create_app()
db.drop_all(app=app)
db.create_all(app=app)
