#!/usr/bin/env bash

# Bootstrap a chef-server ...
# - Install chef-server package
# - Configure it
# - Test it
#

HOME_DIR=/root
echo "Installing chef-server (11.0.12-1), git"
dpkg -i /vagrant/chef-server_11.0.12-1.ubuntu.12.04_amd64.deb
apt-get install git -y
apt-get install vim -y

# copy chef-server.rb to right location
#   - Also rabbitmq needs to listen at 0.0.0.0 address
#     instead of 127.0.0.1
echo "Copying chef-server.rb ..."
mkdir -p /etc/chef-server/
cp /vagrant/chef-server.rb /etc/chef-server/chef-server.rb 

# configure chef-server .. Now we can access webui
echo "Configuring chef-server..."
chef-server-ctl reconfigure
ret=$?
if [ $ret -ne 0 ] ; then
   echo "Error: Cannot configure chef-server..."
   exit 1
fi

# unit test to check if all got installed ok
chef-server-ctl test 
ret=$?
if [ $ret -ne 0 ] ; then
   echo "Error: chef-server tests failed ..."
   exit 2
fi

# create ssh keys for paswordless access
ssh-keygen -t rsa -N "" -f $HOME_DIR/.ssh/id_rsa
cp $HOME_DIR/.ssh/id_rsa.pub /vagrant
cp $HOME_DIR/.ssh/id_rsa /vagrant
cat $HOME_DIR/.ssh/id_rsa.pub >> $HOME_DIR/.ssh/authorized_keys

#
# Chef Client:
#
echo "Installing chef-client (11.04)"
dpkg -i /vagrant/chef_11.4.0-1.ubuntu.11.04_amd64.deb
mkdir $HOME_DIR/.chef

# copy certs
cp /etc/chef-server/chef-validator.pem $HOME_DIR/.chef
cp /etc/chef-server/admin.pem $HOME_DIR/.chef
cp /etc/chef-server/chef-validator.pem /vagrant
cp /etc/chef-server/admin.pem /vagrant

# copy the knife.rb template
cp /vagrant/knife.rb $HOME_DIR/.chef

# check chef-client can talk to chef-server
knife user list
ret=$?
if [ $ret -ne 0 ] ; then
   echo "Error: knife command doesnt work ... config issue?"
   exit 3
fi

# clone contrail-chef
git clone https://github.com/Juniper/contrail-chef.git
ret=$?
if [ $ret -ne 0 ] ; then
   echo "Error: contrail-chef repo cloning failed ..."
   exit 4
fi

# upload roles
knife role from file contrail-chef/roles/*.json

# upload cookbooks
knife cookbook upload -o contrail-chef/cookbooks contrail

# create a client and copy pem
knife client create test_client -a -d > pem.txt
sed -n '/^-----BEGIN.*$/,/^-----END.*$/p' pem.txt > $HOME_DIR/.chef/test_client.pem

sed -i 's/admin/test_client/g' $HOME_DIR/.chef/knife.rb

# create a node
knife node create test_client -d

# run chef-client so chef-server gets the node ipaddress
echo "Starting the knife-status check"
STATUS=0
while [  $STATUS -eq 0 ]; do
    chef-client -c $HOME_DIR/.chef/knife.rb

    out=`knife status`
    echo "The knife-status output is: " $out

    ret=`echo "$out" | awk -F "," '{print NF-1}'`
    echo "The return is: " $ret
    if [ $ret -ge 4 ]; then
        break
    fi
    sleep 5
done

# add the roles to the node
#knife node run_list add test_client 'role[contrail-openstack]'
#knife node run_list add test_client 'role[contrail-database]'
#knife node run_list add test_client 'role[contrail-config]'
#knife node run_list add test_client 'role[contrail-control]'
#knife node run_list add test_client 'role[contrail-analytics]'
#knife node run_list add test_client 'role[contrail-webui]'
#knife node run_list add test_client 'role[contrail-compute]'

echo "!!! Finished !!!"
