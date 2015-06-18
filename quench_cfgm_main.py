#!/usr/bin/env python

import ConfigParser
import os
import sys

_CONFIG_FILE_NAME = "config/q_config.ini"
_VAGRANT_FILE_NAME = "gen/Vagrantfile"

class QuenchCfgm(object):
    def __init__(self, args_str=None):
        self.config = ConfigParser.ConfigParser()
        self.config.read(_CONFIG_FILE_NAME)
        self._curr_dir = os.getcwd()

        self._read_options()
        self._create_vagrant_file()
        self._setup_host()
        self._setup_nodes()
        self._roles_update()
        self._provision_nodes()

    def _read_options(self):
        try:
            self.setup_host = self.config.getboolean('DEFAULT', 'setup_host')
        except ConfigParser.NoOptionError:
            self.setup_host = True
        print("Read Option \"setup_host=%s\"" %(self.setup_host))

        try:
            self.setup_nodes = self.config.getboolean('DEFAULT', 'setup_nodes')
        except ConfigParser.NoOptionError:
            self.setup_nodes = True
        print("Read Option \"setup_nodes=%s\"" %(self.setup_nodes))

        try:
            self.vm_mem = self.config.get('DEFAULT', 'vm_memory')
        except ConfigParser.NoOptionError:
            self.vm_mem = 4096
        print("Read Option \"vm_memory=%s\"" %(self.vm_mem))

        try:
           self.num_vms = self.config.getint('DEFAULT', 'num_nodes')
        except ConfigParser.NoOptionError:
            self.num_vms = 1
        print("Read Option \"num_vms=%d\"" %(self.num_vms))

        try:
            self.box_name = self.config.get('DEFAULT', 'box_name')
        except ConfigParser.NoOptionError:
            self.box_name = "precise"
        print("Read Option \"box_name=%s\"" %(self.box_name))

        try:
            self.chef_prov = self.config.getboolean('DEFAULT', 'chef_prov')
        except ConfigParser.NoOptionError:
            self.chef_prov = True
        print("Read Option \"chef_prov=%s\"" %(self.chef_prov))

        try:
            roles = self.config.get('DEFAULT', 'roles')
        except ConfigParser.NoOptionError:
            roles = "contrail_database,contrail_config"
        print("Read Option \"roles=%s\"" %(roles))
        self.roles = roles.split(',')

    def write(self, fd, gen_str):
        fd.write("%s\n" %(gen_str))

    def _create_vagrant_file(self):
        fd = open(_VAGRANT_FILE_NAME, 'w')
        fd.truncate()

        self.write(fd, "# -*- mode: ruby -*-")
        self.write(fd, "# vi: set ft=ruby :")
        self.write(fd, "")
        self.write(fd, "# All Vagrant configuration is done below. The \"2\" in Vagrant.configure")
        self.write(fd, "# configures the configuration version (we support older styles for")
        self.write(fd, "# backwards compatibility). Please don't change it unless you know what")
        self.write(fd, "# you're doing.")
        self.write(fd, "Vagrant.configure(2) do |config|")
        self.write(fd, "  # The most common configuration options are documented and commented below.")
        self.write(fd, "  # For a complete reference, please see the online documentation at")
        self.write(fd, "  # https://docs.vagrantup.com.")
        self.write(fd, "")
        self.write(fd, "  config.vm.define \"chefserver\" do |chefserver|")
        self.write(fd, "    chefserver.vm.box = \"%s\"" %(self.box_name))
        self.write(fd, "    chefserver.vm.hostname = \"chefserver\"")
        self.write(fd, "    chefserver.vm.provision :shell, :path => \"scripts/bootstrap_chefserver.sh\"")
        self.write(fd, "    chefserver.vm.network \"private_network\", ip: \"10.0.33.10\"")
        self.write(fd, "    chefserver.vm.network \"forwarded_port\", guest: 80, host: 8080")
        self.write(fd, "    chefserver.ssh.username = \"root\"")
        self.write(fd, "    chefserver.ssh.password = \"vagrant\"")
        self.write(fd, "    chefserver.ssh.insert_key = \"true\"")
        self.write(fd, "  end")
        self.write(fd, "")
        node_num = 10
        for index in range(self.num_vms):
            node_num = node_num + 1
            node_name = 'node' + str(node_num)
            self.write(fd, "  config.vm.define \"%s\" do |%s|" %(node_name, node_name))
            self.write(fd, "    %s.vm.box = \"%s\"" %(node_name, self.box_name))
            self.write(fd, "    %s.vm.hostname = \"%s\"" %(node_name, node_name))
            self.write(fd, "    %s.vm.provision :shell, :path => \"scripts/bootstrap_node.sh\"" %(node_name))
            self.write(fd, "    %s.vm.network \"private_network\", ip: \"10.0.33.%s\"" %(node_name, node_num))
            self.write(fd, "    %s.vm.network \"forwarded_port\", guest: 80, host: 90%s" %(node_name, node_num))
            self.write(fd, "    %s.ssh.username = \"root\"" %(node_name))
            self.write(fd, "    %s.ssh.password = \"vagrant\"" %(node_name))
            self.write(fd, "    %s.ssh.insert_key = \"true\"" %(node_name))
            self.write(fd, "    %s.ohai.primary_nic = \"eth1\"" %(node_name))
            if self.chef_prov == True:
                self.write(fd, "    %s.vm.provision :chef_client do |chef|" %(node_name))
                self.write(fd, "      chef.chef_server_url = \"https://10.0.33.10\"") 
                self.write(fd, "      chef.validation_client_name = \"chef-validator\"") 
                self.write(fd, "      chef.validation_key_path = \"chef-validator.pem\"") 
                self.write(fd, "      #chef.add_role \"contrail-database\"") 
                self.write(fd, "      #chef.add_role \"contrail-config\"") 
                self.write(fd, "      chef.delete_node = true") 
                self.write(fd, "      chef.delete_client = true") 
                self.write(fd, "    end")
            self.write(fd, "  end")
            self.write(fd, "")

        self.write(fd, "  config.vm.provider \"virtualbox\" do |vb|")
        self.write(fd, "    # Customize the amount of memory on the VM:")
        self.write(fd, "    vb.memory = \"%s\"" %(self.vm_mem))
        self.write(fd, "  end")
        self.write(fd, "end")

    def _setup_host(self):
        if not self.setup_host:
            return

        print("Changing Directory to: %s/downloads" %(self._curr_dir))
        os.chdir("%s/downloads" %(self._curr_dir))
        print("Installing vagrant package")
        os.system("dpkg -i vagrant_1.7.2_x86_64.deb")
        print("Installing virtualbox package")
        os.system("dpkg -i virtualbox-4.3_4.3.28-100309~Ubuntu~raring_amd64.deb")
        print("Installing chef-client package")
        os.system("dpkg -i chef_11.4.0-1.ubuntu.11.04_amd64.deb")
        print("Installing vagrant ohai plugin")
        os.system("vagrant plugin install vagrant-ohai")
        print("Adding box image")
        os.system("vagrant box add precise precise-server-cloudimg-amd64-vagrant-disk1.box")

    def _setup_nodes(self):
        if not self.setup_nodes:
            return
        print("Changing Directory to: %s/gen" %(self._curr_dir))
        os.chdir("%s/gen" %(self._curr_dir))
        print("Running Vagrant up on chef-server")
        os.system("vagrant up chefserver")
        print("copying admin.pem for knife to work")
        os.system("vagrant ssh chefserver -c \"cp /etc/chef-server/admin.pem /vagrant/\"")
        os.system("mkdir -p /root/.chef/")
        os.system("cp admin.pem /root/.chef/admin.pem")
        print("Running vagrant up on node11-node1%s" %(self.num_vms))
        os.system("vagrant up /node*/")
        
    def _roles_update(self):
        if not self.setup_nodes:
            return
        print("Checking knife status chef-server")
        node_num = 11
        for index in range(self.num_vms):
            node_name = 'node' + str(node_num+index)
            os.chdir(self.vagrant_root_dir)
            os.system("bash -x knife_check.sh %s" %(node_name))

        print("Updating roles in chef-server")
        node_num = 11
        for index in range(self.num_vms):
            node_name = 'node' + str(node_num+index)
            for role in self.roles:
                print("Updating run_list to add role %s for node %s" %(role, node_name))
                os.system("knife node run_list add %s 'role[%s]'" %(node_name, role))

    def _provision_nodes(self):
        if not self.setup_nodes:
            return
        print("Provisioning nodes ... ")
        node_num = 11
        for index in range(self.num_vms):
            node_name = 'node' + str(node_num+index)
            print("provisioning node %s ..." %(node_name))
            os.system("vagrant provision %s" %(node_name))
            os.system("vagrant ssh %s -c \"openstack-config --set /etc/neutron/neutron.conf DEFAULT auth_strategy noauth\"" %(node_name))
            os.system("vagrant ssh %s -c \"openstack-config --del /etc/neutron/neutron.conf DEFAULT service_plugins\"" %(node_name))
            os.system("vagrant ssh %s -c \"service neutron-server restart\"" %(node_name))


def main(args_str=None):
    QuenchCfgm(args_str)
# end main

if __name__ == "__main__":
    main()
