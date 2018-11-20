# -*- coding: utf-8 -*-
"""Admin API endpoints.

This module implements the administration endpoints for the REST API. Currently
included are:

SetupApi: Invoked to set up the eMoL instance

"""

# standard library imports
import os
import grp
import pwd
import json
import yaml
from slugify import slugify
from uuid import uuid4

# third-party imports
from flask import request, current_app
from flask_restful import Resource

# application imports
from emol.models import Authorization, Config, Discipline, Marshal, Role, User, UserRole


@current_app.api.route('/api/setup')
class SetupApi(Resource):
    """The eMoL instance setup endpoint.

    Permitted methods: POST

    """

    @staticmethod
    def post():
        """POST method handler.

        Receive JSON object of setup data, and perform setup of the instance

        The form data must contain a 'data' key that contains a JSON object for
        the instance configuration data.

        The JSON object should include:

            admin_emails:   A list of email addresses that must correspond to
                            Google accounts. Each address will be given system
                            admin privilege

            disciplines:    Array of disciplines that the eMoL instance will
                            track. This array contains all authorization and
                            marshal data for the discipline as well.

                            Each array element is an object:
                            {
                                name,
                                slug,
                                authorizations: {
                                    slug: name,
                                    slug: name,
                                    ...
                                },
                                marshals: {
                                    slug: name,
                                    slug: name,7
                                    ...
                                }
                            }

                            In each case, name is a printable representation and
                            slug is database- and programmatic-friendly label.
                            For example:

                            discipline:
                                name = 'Armoured Combat'
                                slug = 'armoured-combat'

                                name = 'Rapier'
                                slug = 'rapier'

                            authorization:
                                name = 'Two Weapon'
                                slug = 'two-weapon'

                                name = 'Heavy Rapier'
                                slug = 'heavy-rapier'

                            marshal:
                                name = 'Marshal'
                                slug = 'marshal'

                                name = 'Cut & Thrust Marshal'
                                slug = 'cut-thrust-marshal'


        Roles will be configured based on the contents of USER_ROLES
        (see emol.roles)

        It is currently assumed that any changes to roles or disciplines will be
        handled through SQL

        Returns:
            400: Any required data is missing or invalid
            200: All is well

        """
        # TODO: Enforce key length and return error if it is bad
        # TODO: Validate the data form and format
        if 'file' not in request.files:
            return redirect(request.url)

        SetupApi.setup(request.files['file'])

    @staticmethod
    def test_setup(json_str):
        SetupApi.setup(json.loads(json_str))

    @staticmethod
    def setup(data):
        """Set up eMoL.

        Args:
            data: a File or FileStorage type object referring to a YAML
                  file containing configuration data
        """
        current_app.logger.debug('Entering setup API')

        try:
            if Config.get('is_setup'):
                current_app.logging.error('eMoL is already configured')
                return
        except Exception as exc:
            print(exc)
            # No config table, definitely not set up
            pass

        # Set up the database
        current_app.logger.debug('Set up db tables')
        current_app.db.create_all()

        # card and waiver date states
        current_app.logger.debug('Set card and waiver states')

        current_app.logger.debug('Set up roles')
        # Roles from the role definitions in roles.py
        print(Role.USER_ROLES)
        for role in Role.USER_ROLES:
            print(role)
            slug = role.get('slug')

            user_role = Role(
                name=role.get('name'),
                slug=role.get('slug'),
                discipline=None if slug in Role.GLOBAL_ROLES else False
            )
            print(user_role)
            current_app.db.session.add(user_role)

        # Admin role
        print('admin_role')
        admin_role = Role(
            name="admin",
            slug="admin",
            discipline_id=None
        )
        print(admin_role)
        current_app.db.session.add(admin_role)

        # Read the YAML config file
        config = yaml.load(data)
        default_reminders = config.get('card_reminders')

        # Create system admin users
        for email in config.get('admin_emails'):
            if User.query.filter(User.email == email).one_or_none() is not None:
                continue

            user = User(
                email=email,
                system_admin=True
            )
            current_app.db.session.add(user)

            # Grant ultimate cosmic power
            user_role = UserRole(
                user=user,
                role=admin_role,
                discipline=None
            )
            current_app.db.session.add(user_role)

        # Write the keyfile and set permissions
        current_app.logger.debug('Set up db keyfile')
        key_file = current_app.config.get('KEYFILE_PATH')
        with open(key_file, 'w') as keyfile:
            keyfile.write(uuid4().hex)

        current_app.logger.debug('Set keyfile permissions')
        # Encryption keyfile is readable only by the user that runs the app
        os.chmod(key_file, 0o600)

        owner = current_app.config.get('KEYFILE_OWNER')
        uid = pwd.getpwnam(owner).pw_uid
        gid = grp.getgrnam(owner).gr_gid
        current_app.logger.info('Set ownership to {0}, uid={1}, gid={2}'
                                .format(owner, uid, gid))
        os.chown(key_file, uid, gid)

        # Set up the disciplines
        current_app.logger.debug('Set up disciplines')
        for discipline in config.get('disciplines'):
            slug = slugify(name)
            current_app.logger.debug('Set up {0} ({1})'
                                     .format(discipline.get('name'), slug))

            new_discipline = Discipline(
                name=discipline.get('name'),
                slug=discipline.get('slug'),
                _reminders_at=json.dumps(discipline.get('reminders_at', default_reminders))
            )

            current_app.db.session.add(new_discipline)

            for name in discipline.get('authorizations'):
                slug = slugify(name)
                authorization = Authorization(
                    name=name,
                    slug=slug,
                    discipline=new_discipline
                )
                current_app.db.session.add(authorization)

            for name in discipline.get('marshals'):
                slug = slugify(name)
                marshal = Marshal(
                    name=name,
                    slug=slug,
                    discipline=new_discipline
                )
                current_app.db.session.add(marshal)

        Config.set('waiver_reminders', json.dumps(default_reminders))
        Config.set('card_reminders', [30, 60])
        Config.set('is_setup', True)
        current_app.db.session.commit()

        current_app.logger.debug('Setup complete: {0}'.format(Config.get('is_setup')))
