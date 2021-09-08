# import click
from flask import current_app, g
from flask_caching import Cache  # pylint: disable=

# from flask.cli import with_appcontext


def get_cache():
    """get cache"""
    if 'cache' not in g:
        g.cache = Cache(current_app)#pylint:disable=assigning-non-slot
    return g.cache
