from authomatic.providers import oauth2
import authomatic

##################################################################
# Do NOT leave debug on in production!
##################################################################
DEBUG = True

##################################################################
# Database config
##################################################################
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://emol:qwert@localhost/emol'

##################################################################
# Format for log entries
# See https://docs.python.org/3/library/logging.html#logrecord-attributes
##################################################################
LOG_FORMAT = '%(asctime)-15s %(message)s'

##################################################################
# Authomatic configuration
##################################################################
AUTHOMATIC_CONFIG = {
    'google': {
        'class_': oauth2.Google,
        'id': authomatic.provider_id(),
        'consumer_key': '<google key>',
        'consumer_secret': '<google secret>',
        'scope': oauth2.Google.user_info_scope
    },
}

##################################################################
# Secrets
# They should be different
# They should be something long, like a UUID
# You could get UUIDs here: https://www.uuidgenerator.net/
##################################################################
# This one is for the Flask framework
SECRET_KEY = '123456'
# This one is needed by Authomatic
AUTHOMATIC_SECRET = 'top.secret.'
# This one is used by eMoL
HASH_SALT = 'mmmm, salty'

##################################################################
# AWS credential info.
# These three items can also be stored in ~/.aws/credentials
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file
##################################################################
# AWS Region that your stuff is in
AWS_REGION = 'ca-central-1'
# AWS access key for the IAM account with privileges required by eMoL
#
# THIS SHOULD NOT BE YOUR ROOT IAM USER!
#
# Create an eMoL specific user  that has a policy granting only the
# required privileges and generate 
AWS_ACCESS_KEY = 'AKIAABCDEF'
# AWS secret key for the above access key
AWS_SECRET_KEY = '<some secret key>'

##################################################################
# Encryption key, stored in Amazon KMS
##################################################################
# ARN of a KMS key to use for encryption of data
EMOL_KMS_KEY = 'arn:aws:kms:...'

##################################################################
# Mail settings
##################################################################
# FQDN or IP address of your mail server
MAIL_HOST = '<your SMTP server>'
# Port to use on mail server, defaults to 25 if omitted
MAIL_PORT = 25
# SMTP username if required
MAIL_USERNAME = '<SMTP user>'
# SMTP password if required
MAIL_PASSWORD = '<SMTP password>'
# Email sent by eMoL will come from this sender
MAIL_DEFAULT_SENDER = 'eMoL <emol@example.com>'
# True if your mail server requires SSL
MAIL_USE_SSL = True/False
# True if your mail server requires TLS
MAIL_USE_TLS = True/False