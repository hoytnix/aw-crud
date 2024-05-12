import click

from {{cookiecutter.app_name}}.app import create_app


@click.command()
@click.option('--environment', '-e', default=None)
def cli(environment):
    app = create_app(environment)

    use_debugger = app.debug
    try:
        # Disable Flask's debugger if external debugger is requested
        use_debugger = not (app.config.get('DEBUG_WITH_APTANA'))
    except:
        pass
    app.run(use_debugger=use_debugger,
            debug=app.debug,
            use_reloader=use_debugger,
            host='0.0.0.0')
