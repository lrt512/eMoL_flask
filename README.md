# eMoL

An online authorization card manager for SCA usage.

In this repository, eMoL is configured for the Kingdom of Ealdormere and has
handlers for armoured combat and rapier combat. It should be easily modifiable
for any Kingdom and its authorization system.

## Features
* Web-based cards that can be pulled up on smartphone or tablet for easy view
* Cards indicate both waiver expiry date and card expiry date
* Cards are printable for those who do not wish to tote an electronic device
around an event
* Configurable email reminders for card and waiver expiry (default 60 days, 30
days, 14 days)
* Warrant rosters can be generated on demand
* Allows for combat disciplines that do not use authorizations (e.g. archery),
and can simply track marshal status
* Configurable access for different users. Each user can be selectively granted
access to combatant info, authorization info (per discipline), and marshal
status (per discipline)

## Security and Privacy
* Combatant personal info is stored encrypted (AES-256) in the datastore
(see documentation/security.md)
* eMoL has a privacy policy that is sent by email to every combatant that is
added to the system. Each combatant is given an opt-out if they wish for their
records to be kept manually.
* Users (Kingdom Marshals, MoLs) are handled through Google Authentication

## Technology Stack
* Vagrant
* Flask (with Flask_Login, Authomatic, Flask-RESTful)
* SQLAlchemy
* MySQL
* SQLite3 (for unit tests)
* Python 3.5
* Encryption via PyCrypto
