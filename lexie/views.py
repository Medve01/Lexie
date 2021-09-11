# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask import Blueprint, render_template, request
from jinja2 import TemplateNotFound

from lexie.devices.LexieDevice import get_all_devices

# Register blueprint
ui_bp = Blueprint('ui', __name__, url_prefix='/ui')


# App main route + generic routing
@ui_bp.route('/', defaults={'path': 'index.html'})
@ui_bp.route('/<path>')
def index(path):
    """ renders default ui page """
    try:

        # Detect the current page
        segment = get_segment( request )
        devices = get_all_devices()

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( path, segment=segment, devices=devices )

    except TemplateNotFound:
        return render_template('page-404.html', segment=segment), 404

# Helper - Extract current page name from request
def get_segment( ui_request ):
    """ whatever """
    try:
        segment = ui_request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except: # pylint: disable=bare-except # pragma nocover
        return None # pragma nocover
