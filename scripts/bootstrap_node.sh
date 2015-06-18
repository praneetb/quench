#!/usr/bin/env bash

#
# Setup Repo:
#

file="bootstrapped"
if [ -f "$file" ]
then
  exit
fi

echo "Installing contrail image ... "
dpkg -i /vagrant/contrail-install-packages_2.20-45~icehouse_all.deb

echo "setting up repo ..."
/opt/contrail/contrail_packages/setup.sh

apt-get install tzdata=2015c-0ubuntu0.12.04 -y --force-yes

#
# Chef Client:
#

HOME_DIR=/root
hostname=$(hostname)

# set up ssh keys
cp /vagrant/id_rsa $HOME_DIR/.ssh/
cp /vagrant/id_rsa.pub $HOME_DIR/.ssh/

echo "10.0.33.10 chefserver chefserver" >> /etc/hosts

touch $file
echo "!!! Finished !!!"
