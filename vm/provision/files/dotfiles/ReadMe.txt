This directory contains hidden files to be installed in the vm for
user vagrant. E.g, .profile will become a symbolic link in the vm:

        /home/vagrant/.profile => /vagrant/provision/files/dotfiles/.profile

Only hidden files in this directory are linked, i.e, those matching ".??*".
