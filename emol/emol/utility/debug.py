# -*- coding: utf-8 -*-
"""Debugging helpers."""

# standard library imports
import os
from inspect import currentframe, getouterframes

# third-party imports
from flask import current_app

# application imports

FILE_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(FILE_DIR))


def dprint(expr, **kwargs):
    """Debug print.

    Does nothing if DEBUG is False
    Use the standard print function to augment with filename and line number
    Truncates the filename to remove everything preceding the package root

    Args:
        expr: The message, which may be a format string
        **kwargs: Keyword arguments for expr

    """
    if current_app.config.get('DEBUG') is False:
        return

    # We want the previous frame for the caller.
    # getouterframes returns a tuple:
    # (frame, filename, line_number, function_name, lines, index)
    frame_data = getouterframes(currentframe())[1]

    print("({_file}:{_line}) {formatted}".format(
        _file=frame_data[1].replace(BASE_DIR, ''),
        _line=frame_data[2],
        formatted=str(expr).format(kwargs)))
