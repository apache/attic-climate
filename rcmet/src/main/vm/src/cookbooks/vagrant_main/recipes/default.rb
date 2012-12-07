# APT Package Management --------------------------------------------
# Install the APT package management tool, and then install any
# packages that we will need to have to complete the buildout.
#
include_recipe "apt"
include_recipe "build-essential"
gem_package "ruby-shadow" do
  action :install
end

# User Creation -----------------------------------------------------
# Create a user account for the 'rcmet' user
#
user "rcmet" do
  comment "RCMET user"
  uid 1001
  #gid "users"
  home "/usr/local/rcmet"
  shell "/bin/bash"
  #password "1bob1bob"
end

directory "/usr/local/rcmet" do
  mode "0777"
end


# Python Environment Setup ------------------------------------------
# Install Python and package management tools 'pip' and 'virtualenv'.
# Then create a virtual environment in  the 'rcmet' user's home 
# directory, into which all RCMET python code and dependencies can be 
# installed.
#
include_recipe "python"

python_virtualenv "/usr/local/rcmet/python-env" do
  owner "rcmet"
  group "rcmet"
  action :create
end

# Apache Web Server Configuration -----------------------------------
# Install the Apache2 HTTPD Web Server, and configure a virtual host
# for the RCMET web application.
#
include_recipe "apache2"

execute "disable-default-site" do
  command "sudo a2dissite default"
  notifies :reload, resources(:service => "apache2"), :delayed
end

web_app "rcmet" do
  template "rcmet.conf.erb"
  notifies :reload, resources(:service => "apache2"), :delayed
end
