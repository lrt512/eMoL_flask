# Email

eMoL sends a fair bit of email. This can be a bit of a pain during development
and testing. To alleviate this, the development VM installs
[mailcatcher](https://mailcatcher.me/).

To read mail sent by eMoL in the development VM, point your browser at
[http://localhost:8025](http://localhost:8025)

*Note* Most of the unit tests use a bit of magic to not send any actual email
and instead just detect that an email would be sent.

If using mailcatcher on a staging server, there's a ```supervisord``` conf
 file for it in [emol/vm/provision/files/etc/supervisor/conf.d](emol/vm/provision/files/etc/supervisor/conf.d)