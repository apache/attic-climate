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

help()
{
cat << ENDHELP

Easy OCW assists with the building of the Apache Open Climate Workbench and 
its dependencies.

Flags:
    -h  Display this help message.
    -e  Install and configure a virtualenv environment before installation.
    -q  Quiet install. User prompts are removed (when possible).

It is recommended that you pass -e when running this script. If you don't, 
parts of this installation will pollute your global Python install. 
If you're unsure, pass -e just to be safe!

N.B. This install script has been tested against Ubuntu 12.04 and 14.04.
Please report problems with this script to dev@climate.apache.org
ENDHELP
}

header()
{
    echo
    echo $1
}

task()
{
    echo " - " $1
}

subtask()
{
    echo "     " $1
}

echo
echo "---------------------------------------------------------------------------"
echo "                         Welcome to Easy OCW"
echo "---------------------------------------------------------------------------"
echo

WITH_VIRTUAL_ENV=0
WITH_HOMEBREW=0
WITH_INTERACT=1

while getopts ":h :e :q" FLAG
do
    case $FLAG in
        h)
            help
            exit 1
            ;;
        e)
            WITH_VIRTUAL_ENV=1
            ;;
        q)
            WITH_INTERACT=0
            ;;
        ?)
            help
            exit 1
            ;;
    esac
done

if [ $WITH_INTERACT == 1 ]; then
cat << ENDINTRO
A number of dependencies for OCW will now be installed. Please check the wiki
for a complete list of dependencies. Additionally, please read the wiki for
useful installation guidelines and information that may be pertinent to your
situation. All of this can be found at http://s.apache.org/3p2

ENDINTRO

if [ $WITH_VIRTUAL_ENV != 1 ]; then
cat << VIRTUALENV_WARNING
It is highly recommended that you allow Easy OCW to install the dependencies
into a virtualenv environment to ensure that your global Python install is
not affected. If you're unsure, you should pass the -e flag
to this script. If you aren't concerned, or you want to create your own
virtualenv environment, then feel free to ignore this message.

VIRTUALENV_WARNING
fi

read -p "Press [ENTER] to begin installation ..."
echo -n "Please specify a full path to where your OCW download is then press [ENTER] ..."
read ocw_path
fi

header "Checking for pip ..."
if [ ! command -v pip >/dev/null 2>&1 ]; then
    task "Unable to locate pip."
    task "Installing Pip"
    sudo apt-get install python-pip >> install_log
    subtask "done"
fi

if [ $WITH_VIRTUAL_ENV == 1 ]; then
    header "Setting up a virtualenv ..."

    # Check if virtualenv is installed. If it's not, we'll install it for the user.
    if ! command -v virtualenv >/dev/null 2>&1; then
        task "Installing virtualenv ..."
        curl -L -o virtualenv.py https://raw.github.com/pypa/virtualenv/master/virtualenv.py
        subtask "done"
    fi

    # Create a new environment for OCW work
    task "Creating a new environment ..."
    python virtualenv.py ocw
    . ocw/bin/activate
    subtask "done"
fi

# Install Continuum Analytics Anaconda Python distribution. This gives
# almost all the dependencies that OCW needs in a single, easy to
# install package.

header "Installing Anaconda Python distribution ..."
echo
echo "*** NOTE *** When asked to update your PATH, you should respond YES."
read -p "Press [ENTER] to continue ..."

cd
task "Downloading Anaconda ..."
wget -O Anaconda-1.9.2-Linux-x86_64.sh "http://repo.continuum.io/archive/Anaconda-1.9.2-Linux-x86_64.sh" 2> install_log
subtask "done"

task "Installing ..."
bash Anaconda-1.9.2-Linux-x86_64.sh
export PATH="${HOME}/anaconda/bin:$PATH"
subtask "done"

# Install Basemap. Conda cannot be used for this install since
# it fails to analyse the dependencies (at the time of writing). This
# will install it manually. At some point, this should be replaced with
# 'conda install basemap' once it is working again!
header "Handling Basemap install ..."

cd
task "Downloading basemap ..."
wget -O basemap-1.0.7.tar.gz "http://sourceforge.net/projects/matplotlib/files/matplotlib-toolkits/basemap-1.0.7/basemap-1.0.7.tar.gz/download" 2> install_log
tar xzf basemap-1.0.7.tar.gz >> install_log
subtask "done"

# Install GEOS
task "Installing GEOS dependency ..."
cd basemap-1.0.7/geos-3.3.3
export GEOS_DIR=/usr/local
./configure --prefix=$GEOS_DIR >> install_log
sudo make >> install_log
sudo make install >> install_log
subtask "done"

# Install basemap
task "Installing Basemap ..."
cd ..
python setup.py install >> install_log
subtask "done"

cd

# Install miscellaneous Python packages needed for OCW. Some of these
# can be installed with Conda, but since none of them have an annoying
# compiled component we just installed them with Pip.
header "Installing additional Python packages"
pip install -r ocw-pip-dependencies.txt >> install_log

# Ensure that the climate code is included in the Python Path
header "Updating PYTHONPATH with ocw executables ..."
echo "export PYTHONPATH=${ocw_path}:${ocw_path}/ocw" >> ${HOME}/.bashrc
subtask "done"
