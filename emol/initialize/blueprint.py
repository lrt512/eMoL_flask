# -*- coding: utf-8 -*-
"""Initialize application blueprints."""

# standard library imports
import os
from importlib import import_module

# third-party imports
from flask import current_app


def init_blueprints():
    """Register blueprints on the app.

    Walk the views directory and programmatically try to load .py files as
    modules. Once loaded, look for a blueprint declaration and register it
    if present.
    """
    current_app.logger.info('Initialize blueprints')
    root_dir = os.path.dirname(os.path.dirname(__file__))
    view_dir = os.path.join(root_dir, 'views')

    for root, dirs, files in os.walk(view_dir):
        basename = os.path.basename(root)
        if basename == 'views':
            # Don't forget any files in emol/views itself
            module_base = 'emol.views'
        else:
            # emol/views/foo
            module_base = 'emol.views.{}'.format(basename)

        for file_ in files:
            if not file_.endswith('.py') or '__init__' in file_:
                continue

            module = '{}.{}'.format(module_base, os.path.splitext(file_)[0])
            mod = import_module(module)
            if mod is None:
                continue

            blueprint = getattr(mod, 'BLUEPRINT', None)
            if blueprint is None:
                continue

            current_app.register_blueprint(blueprint)
