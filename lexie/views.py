
# Flask modules
import logging
import os

from flask import Blueprint, redirect, render_template, request
from jinja2 import TemplateNotFound

from .smarthome.LexieDevice import (LexieDevice, LexieDeviceType,
                                    get_all_devices)

# Register blueprint
ui_bp = Blueprint('ui', __name__, url_prefix='/ui')

# Helper - Extract current page name from request
def get_segment( path ):
    """ gets the word between http://127.0.0.1/ui/ and .html """
    try:
        segment = path.split('/')[-1]
        if segment == '':
            segment = 'dashboard' #pragma: nocover
        return segment
    except: # pylint: disable=bare-except # pragma nocover
        return None # pragma nocover

def get_drivers():
    """ Fetches the available drivers in the drivers folder"""
    drivers=[]
    elements=os.listdir('./drivers')
    for item in elements:
        if item[0]!="_":
            modules = os.listdir('./drivers/' + item)
            for module in modules:
                if module[0] != "_":
                    drivers.append(item + " - " + module[:-3])
    return drivers

# App main route + generic routing
@ui_bp.route('/', defaults={'path': 'dashboard'})
@ui_bp.route('/<path>')
def index(path):
    """ renders default ui page """
    try:

        # Detect the current page
        segment = get_segment( path )
        logging.info(segment)
        if segment in ('device-list','dashboard', 'index'):
            devices = get_all_devices()
            return render_template( segment + '.html', segment=segment, devices=devices )
        if segment == "add-device":
            # drivers=get_drivers()
            return render_template( segment + '.html', drivers=get_drivers(), segment=segment)
        return render_template( segment + '.html', segment=segment)

        # Serve the file (if exists) from app/templates/FILE.html

    except TemplateNotFound:
        return render_template('page-404.html', segment=segment), 404

@ui_bp.route('/add-device', methods=["POST"])
def add_device():
    """ creates a new LexieDevice based on form data """
    device_data = request.form
    LexieDevice.new(
        device_name=device_data['device_name'],
        device_type=LexieDeviceType(device_data['device_type']),
        device_manufacturer=device_data['device_driver'].split('-')[0].strip(),
        device_product=device_data['device_driver'].split('-')[1].strip(),
        device_attributes={'ip_address': device_data['device_ip']}
    )
    return redirect( '/ui/device-list')
