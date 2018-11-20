# -*- coding: utf-8 -*-
"""Set up custom error handlers."""

# standard library imports

# third-party imports
from flask import render_template, request, Response, current_app

# application imports


def init_error_handlers():
    """Custom error pages for the app."""
    current_app.logger.info('Initialize error handling')

    # pylint really hates these 'unused' decorated functions.
    # In reality, they are callbacks for Flask
    # pylint: disable=unused-variable
    @current_app.errorhandler(404)
    def not_found(error):
        """Custom 404 handler to return error page."""
        current_app.logger.debug(error)
        if len(request.form) > 0:
            # Requests with form data are likely AJAX
            return Response(None, 404)

        return render_template('errors/404.html', http_error=True), 404

    @current_app.errorhandler(403)
    def forbidden(error):
        """Custom 404 handler to return error page."""
        current_app.logger.debug(error)
        return render_template('errors/403.html', http_error=True), 403

    @current_app.errorhandler(401)
    def unauthorized(error):
        """Custom 401 handler to return error page."""
        current_app.logger.debug(error)
        return render_template('errors/401.html', http_error=True), 401

    @current_app.errorhandler(500)
    def uhoh(error):
        """Custom 500 handler to return error page."""
        current_app.logger.error(error)
        return render_template('errors/500.html', http_error=True), 500
