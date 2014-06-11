#!/bin/bash
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# Install some useful/necessary dependencies to make future installs easier
sudo apt-get update
sudo apt-get install -y make
sudo apt-get install -y libblas-dev
sudo apt-get install -y liblapack-dev
sudo apt-get install -y gfortran
sudo apt-get install -y g++
sudo apt-get install -y build-essential
sudo apt-get install -y python-dev 
sudo apt-get install -y ia32-libs --fix-missing
sudo apt-get install -y git
sudo apt-get install -y vim

# GUI related installs
sudo apt-get install -y lightdm

# XFCE
#sudo apt-get install -y xfce4
#sudo apt-get install -y xdg-utils
#sudo apt-get install -y eog

# Ubuntu Unity
sudo apt-get install -y ubuntu-desktop

# Use the Easy-OCW Ubuntu install script to get everything
# else installed!
git clone http://git-wip-us.apache.org/repos/asf/climate.git

# Copy the Easy-OCW install script for Ubuntu
cp climate/easy-ocw/install-ubuntu-12_04.sh .
# Copy the requirements files for conda and pip used by Easy-OCW
cp climate/easy-ocw/*.txt .

bash install-ubuntu-12_04.sh -q

# Set symlink for the UI frontend code
cd climate/ocw-ui/backend
ln -s ../frontend/app app

# Cleanup Anaconda and Basemap downloads from the install script
cd
sudo rm -f Anaconda-1.9.2-Linux-x86_64.sh
sudo rm -f basemap-1.0.7.tar.gz
sudo rm -rf basemap-1.0.7

mkdir /home/vagrant/Desktop

# These links will only work if we're using the Unity desktop.
# If you want to use the XFCE desktop you will need to change
# the references to 'nautilus' to whatever file browser you
# will be using.
cat >/home/vagrant/Desktop/climate.desktop <<CODELINK
[Desktop Entry]
Name=Climate-Code
Icon=utilities-terminal
Exec=nautilus /home/vagrant/climate
Terminal=false
Type=Application
CODELINK

cat >/home/vagrant/Desktop/ui.desktop <<UISTART
[Desktop Entry]
Name=Climate-UI
Icon=utilities-terminal
Exec=/home/vagrant/Desktop/.ui.sh
Terminal=true
Type=Application
UISTART

cat >/home/vagrant/Desktop/.ui.sh <<UIBOOTUP
#!/bin/bash
export PATH=/home/vagrant/anaconda/bin:$PATH
export PYTHONPATH=/home/vagrant/climate:/home/vagrant/climate/ocw
cd ~/climate/ocw-ui/backend && python run_webservices.py
UIBOOTUP

# It is possible that these commands will need to be rerun once
# the desktop environment has been updated. You will notice that
# they aren't recognized as shortcuts if you need to rerun these
# commands. If all is working properly, you should see terminal
# icons with the names listed above (Climate-Code or Climate-UI).
chmod +x ~/Desktop/climate.desktop
chmod +x ~/Desktop/.ui.sh
chmod +x ~/Desktop/ui.desktop
