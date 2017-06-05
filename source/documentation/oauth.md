# OAuth Authentication

eMoL uses [Authomatic](https://github.com/authomatic/authomatic) as its OAuth
provider. In the [sample config file](source/vm/deploy/somehost.com.config.py)
there is default configuration for Google Accounts authorization via OAuth.

Authomatic supports many other authentication providers, see the project
details.

## Setting up Google Authentication
There will need to be a Google account that 'owns' eMoL. The same user that will
be used during setup as the admin user is a good choice. Once that exists,
OAuth can be set up.

* Log into google as the Google account that will own eMoL
* Go to: https://console.developers.google.com
* Select Credentials from the menu
* Create credentials for eMoL
* Set the URL for the login page (http://example.com/login) as an
    authorized redirect URI
* The client ID and client secret go into ```config.py``` as consumer_key and
    consumer_secret in the OAUTH2 section

### Authorized Redirect URI for Development
During development, it's unlikely that there will be an available domain to
associate the development VM with. This is fine. Clever people have set up
certain domains on the Internet to resolve to ```localhost```.

One example of this is ```vcap.me```. If you use ```http://emol.vcap.me:8088```
to access the eMoL development server from a web browser, then you can set
```http://emol.vcap.me:8088/login``` as an authorized redirect URI in the
Google developer console and OAuth will work in your development VM.

### Authorized Redirect URI for Production
When deploying to production, the URI for ```login``` in production will also
need to be added to the list. For example, ```http://emol.ealdormere.ca/login```

It's okay to have multiple redirect URIs active, so it isn't necessary to
remove the development one when deploying live.

Once redirect URIs are set, then logging in to eMoL is simply a matter of
creating Google accounts for the various users of the system.


