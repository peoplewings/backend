#!/bin/bash

ROOT_UID=0 #Only users with UID=0 can execute this script
E_NOROOT=87 #Error if you are not root

if [ ! "$(whoami)" = "root"  ]; then
	echo "Must be root to run this script."
	exit $E_NOROOT
fi

update = "apt-get update -qy"
upgrade = "apt-get upgrade -qy"
python= "apt-get install python 2.7.3 -qy"
postgres= "apt-get install postgresql-9.1 -qy"
postgres_server= "apt-get install postgresql-server-dev-9.1 -qy"
libcurl= "apt-get install libcurl4-gnutls-dev -qy"
python_dev= "apt-get install python2.7-dev -qy"
rubygem= "apt-get install rubygems -qy"
foreman= "gem install foreman -qy"

exit 0