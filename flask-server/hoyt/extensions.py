"""Extensions are instantiated here to prevent circular import dependencies."""

from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_misaka import Misaka

from lib.freezer import Freezer

admin = Admin
db = SQLAlchemy()
md = Misaka(**{'fenced_code': True})

freezer = Freezer
