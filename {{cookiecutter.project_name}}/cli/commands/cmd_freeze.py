import click

from {{cookiecutter.app_name}}.extensions import Freezer
from {{cookiecutter.app_name}}.app import create_app


@click.command()
@click.option('--environment', '-e', default=None)
def cli(environment):
    """ Run PostgreSQL related tasks. """
    app = create_app(environment=environment)
    freezer = Freezer(app)
    freezer.freeze()
