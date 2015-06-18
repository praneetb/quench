log_level                :info
log_location             STDOUT
node_name                'admin'
client_key               '/root/.chef/admin.pem'
validation_client_name   'chef-validator'
validation_key           '/root/.chef/chef-validator.pem'
chef_server_url          'https://10.0.33.10'
syntax_check_cache_path  '/root/.chef/syntax_check_cache'
cookbook_path            [ '~/contrail-chef/cookbooks/' ]
