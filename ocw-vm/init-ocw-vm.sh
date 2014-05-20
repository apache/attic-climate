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
sudo apt-get install -y xfce4
sudo apt-get install -y xdg-utils
sudo apt-get install -y eog

# Use the Easy-OCW Ubuntu install script to get everything
# else installed!
git clone http://git-wip-us.apache.org/repos/asf/climate.git
cp climate/easy_ocw/install-ubuntu-12_04.sh .
bash install-ubuntu-12_04.sh -q
