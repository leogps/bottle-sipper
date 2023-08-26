import json
import os
import sys

YES = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup']

DEFAULT_TEMPLATE_BASE_DIR = 'templates/default/'

APP_NAME = 'bottle-sipper'

APP_LINK = 'https://github.com/leogps/bottle-sipper'


def load_json(json_file_path):
    with open(json_file_path, 'r') as json_file:
        return json.load(json_file)


#
# Loading json files into variables.
#
_current_script_path = os.path.abspath(__file__)

# Get the directory of the current script
_current_script_dir = os.path.dirname(_current_script_path)

_mime_type_extensions_json_file = os.path.join(_current_script_dir, 'static', 'mime_type_extensions.json')
_mime_extension_map = load_json(_mime_type_extensions_json_file)

_icons_json_file = os.path.join(_current_script_dir, 'static', 'icons.json')
_icons = load_json(_icons_json_file)

#
# Loading version
#
_python_version = sys.version


def get_icons():
    return _icons


def get_mime_extensions():
    return _mime_extension_map


def get_python_version():
    return _python_version
