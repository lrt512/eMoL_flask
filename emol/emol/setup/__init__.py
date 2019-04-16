# -*- coding: utf-8 -*-
"""Setup functions

Functions used to set up the eMoL instance from a YAML file.
"""

# standard library imports
import contextlib
import json

# third-party imports
from flask import current_app
from slugify import slugify

# application imports
from emol.models import Authorization, Config, Discipline, Marshal, Role, User, UserRole

"""Application setup.

Receive loaded YAML object of setup data, and perform setup of the instance


    admin_emails:   A list of email addresses that must correspond to
                    Google accounts. Each address will be given system
                    admin privilege

    disciplines:    Array of disciplines that the eMoL instance will
                    track. This array contains all authorization and
                    marshal data for the discipline as well.

                    Each array element is an object:
                    name: Rapier
                    authorizations: 
                        - Heavy Rapier
                        - Cut & Thrust
                        - Two Weapon
                        - Parry Device
                    marshals: 
                        - Marshal

Roles will be configured based on the contents of USER_ROLES
(see emol.roles)

It is currently assumed that any changes to roles or disciplines will be
handled through SQL
"""


def setup(config):
    """Set up eMoL.

    Args:
        config: A dictionary of data as detailed above
    """
    try:
        if Config.get('is_setup'):
            current_app.logger.info('eMoL is set up, truncating tables')
            from sqlalchemy import MetaData
            engine = current_app.db.engine
            meta = MetaData(bind=engine, reflect=True)
            with contextlib.closing(engine.connect()) as con:
                con.execute('SET FOREIGN_KEY_CHECKS=0;')
                trans = con.begin()
                for table in reversed(meta.sorted_tables):
                    current_app.logger.info('truncate: {}'.format(table))
                    con.execute(table.delete())
                trans.commit()
                con.execute('SET FOREIGN_KEY_CHECKS=1;')
            return

    except Exception as exc:
        print(exc)
        raise

    # Set up the disciplines
    current_app.logger.debug('Set up disciplines')
    for name, data in config.get('disciplines').items():
        slug = slugify(name)
        current_app.logger.info('Set up {0} ({1})'.format(name, slug))

        new_discipline = Discipline(
            name=name,
            slug=slug,
            _reminders_at=json.dumps(data.get('reminders_at', [30, 60]))
        )

        current_app.db.session.add(new_discipline)

        for auth_name in data.get('authorizations'):
            auth_slug = slugify(auth_name)
            authorization = Authorization(
                name=auth_name,
                slug=auth_slug,
                discipline=new_discipline
            )
            current_app.logger.info(
                '{} authorization {} ({})'
                    .format(name, auth_name, auth_slug)
            )
            current_app.db.session.add(authorization)

        for marshal_name in data.get('marshals'):
            marshal_slug = slugify(marshal_name)
            marshal = Marshal(
                name=marshal_name,
                slug=marshal_slug,
                discipline=new_discipline
            )
            current_app.logger.info(
                '{} marshal {} ({})'
                    .format(name, marshal_name, marshal_slug)
            )
            current_app.db.session.add(marshal)

    current_app.logger.debug('Set up roles')
    # Roles from the role definitions in roles.py
    for role in Role.USER_ROLES:
        name = role.get('name')
        slug = role.get('slug')
        if slug in Role.GLOBAL_ROLES:
            current_app.logger.info('Global role: {} ({})'.format(name, slug))
            user_role = Role(
                name=name,
                slug=slug,
                discipline=None
            )
            current_app.db.session.add(user_role)
        else:
            # Need to make one role for each discipline
            for discipline in Discipline.query.all():
                current_app.logger.info(
                    '{} role: {} ({})'
                    .format(discipline.name, name, slug)
                )
                user_role = Role(
                    name=name,
                    slug=slug,
                    discipline=discipline
                )
                current_app.db.session.add(user_role)

    # Admin role
    current_app.logger.info('Role admin (admin)')
    admin_role = Role(
        name="admin",
        slug="admin",
        discipline_id=None
    )
    current_app.db.session.add(admin_role)

    # Create system admin users
    for email in config.get('admin_emails'):
        if User.query.filter(User.email == email).one_or_none() is not None:
            continue

        current_app.logger.info('Admin {}'.format(email))
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

    waiver_reminders = config.get('waiver_reminders', [30, 60])
    Config.set('waiver_reminders', waiver_reminders)
    current_app.logger.info('Waiver reminders {}'.format(waiver_reminders))

    card_reminders = config.get('card_reminders', [30, 60])
    Config.set('card_reminders', card_reminders)
    current_app.logger.info('Waiver reminders {}'.format(card_reminders))

    Config.set('is_setup', True)
    current_app.db.session.commit()

    current_app.logger.debug('Setup complete: {0}'.format(Config.get('is_setup')))
