# -*- coding: utf-8 -*-

import os
from server.app.main import create_app
from flask.ext.script import Manager, Shell
from flask.ext.script import Manager, Shell, prompt, prompt_pass
from server.app.utils.populate import create_admin_user
from server.app.extensions import db

if os.path.exists('.env'):
  print('Importing environment from .env...')
  for line in open('.env'):
    var = line.strip().split('=')
    if len(var) == 2:
      os.environ[var[0]] = var[1]


# 通过配置创建 app
app = create_app()
manager = Manager(app)


def make_shell_context():
  return dict(app=app)

manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
@manager.option('-e', '--email', dest='email')
def create_admin(username=None, password=None, email=None):
    """Creates the admin user."""

    if not (username and password and email):
        username = prompt("Username")
        email = prompt("A valid email address")
        password = prompt_pass("Password")

    create_admin_user(username=username, password=password, email=email)


@manager.command
def init_db():
    db.drop_all()
    db.create_all()


@manager.command
def deploy():

  """Run deployment tasks."""
  pass
if __name__ == '__main__':
  manager.run()