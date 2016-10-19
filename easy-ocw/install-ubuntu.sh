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

# Find absolute path to the easy-ocw directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR
ocw_path="$DIR/../climate"

while getopts ":h" FLAG
do
    case $FLAG in
        h)
            help
            exit 1
            ;;
        ?)
            help
            exit 1
            ;;
    esac
done

cat << ENDINTRO
A number of dependencies for OCW will now be installed. Please check the wiki
for a complete list of dependencies. Additionally, please read the wiki for
useful installation guidelines and information that may be pertinent to your
situation. All of this can be found at http://s.apache.org/3p2
ENDINTRO

cat << VIRTUALENV_WARNING
$(tput setaf 1)<-----------------------------[WARNING!]----------------------------------->$(tput sgr 0)
Easy OCW will automatically create a conda environment "venv-ocw".
All the dependencies will be installed in the virtual environment
to ensure that your global Python install is not affected.

Please activate the virtual environment venv-ocw after the script has completed to use OCW.

To activate the virtual environment execute
> source active venv-ocw

To deactivate the virtual environment execute
> source deactivate

VIRTUALENV_WARNING

echo "Easy-OCW script logs" > install_log

# Install Continuum Analytics Miniconda Python distribution. This gives
# almost all the dependencies that OCW needs in a single, easy to
# install package.
header "Installing Miniconda Python distribution ..."

MACHINE_TYPE=`uname -m`
if [ ${MACHINE_TYPE} == 'x86_64' ]; then
	link="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
else
	link="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86.sh"
fi

header "Checking for conda ..."
command -v conda >/dev/null 2>&1 || {
    task "Unable to locate conda."
    if ! [ -f Miniconda-latest-linux.sh ]; then
		task "Downloading Miniconda ..."
		wget -O Miniconda-latest-linux.sh $link >> install_log 2>&1
		subtask "done"
    fi
	task "Installing ..."
	bash Miniconda-latest-linux.sh -b -p $HOME/miniconda
	export PATH="$HOME/miniconda/bin/:$PATH"
	subtask "done"
}

header "Creating venv-ocw environment and installing dependencies"
conda config --add channels conda-forge
conda create --name venv-ocw -y --file ocw-conda-dependencies.txt
task "Activating venv-ocw virtual environment"
source activate venv-ocw

conda config --set always_yes yes
conda update -q conda

header "Conda Information"
echo "------------------------------------------------------------------"
conda info -a

echo
task "Installing python-dev"
sudo apt-get -y install python-dev >> install_log 2>&1
subtask "done"

cd $DIR

header "Installing remaining dependencies via pip"
pip install -r ocw-pip-dependencies.txt
subtask "done"

header "Installing ocw module"

cd ..
python setup.py install
subtask "Finished installing OCW module"

header "For any issues with installation please contact dev@climate.apache.org"
