# -*- coding: utf-8 -*-
"""Initialize application blueprints."""

# standard library imports

# third-party imports
from flask import current_app

# application imports
from emol.views.home import BLUEPRINT as home_blueprint
from emol.views.admin.admin import BLUEPRINT as admin_blueprint
from emol.views.user.user_admin import BLUEPRINT as ua_blueprint
from emol.views.user.user import BLUEPRINT as user_blueprint
from emol.views.officer.officer_admin import BLUEPRINT as oa_blueprint
from emol.views.combatant.combatant_admin import BLUEPRINT as ca_blueprint
from emol.views.combatant.combatant import BLUEPRINT as combatant_blueprint
from emol.views.privacy.privacy_policy import BLUEPRINT as pp_blueprint
from emol.views.admin.setup import BLUEPRINT as setup_blueprint


def init_blueprints():
    """Register blueprints on the app."""
    current_app.logger.info('Initialize blueprints')
    current_app.register_blueprint(home_blueprint)
    current_app.register_blueprint(admin_blueprint)
    current_app.register_blueprint(ua_blueprint)
    current_app.register_blueprint(user_blueprint)
    current_app.register_blueprint(oa_blueprint)
    current_app.register_blueprint(ca_blueprint)
    current_app.register_blueprint(combatant_blueprint)
    current_app.register_blueprint(pp_blueprint)

    current_app.register_blueprint(setup_blueprint)
