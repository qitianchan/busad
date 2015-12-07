# -×- coding:utf-8 -*-
from server.app.models.user import User


def create_admin_user(username, password, email):
    """Creates the administrator user.
    Returns the created admin user.

    :param username: The username of the user.

    :param password: The password of the user.

    :param email: The email address of the user.
    """

    user = User(username=username, password=password)

    user.email = email
    user.save(role=0)
    return user

