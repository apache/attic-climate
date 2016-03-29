
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
ocw_path="${HOME}/climate"

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
$(tput setaf 1)<-----------------------------[WARNING!]----------------------------------->$(tput sgr 0) 
It is highly recommended that you allow Easy OCW to install the dependencies
into a virtualenv environment to ensure that your global Python install is
not affected. If you're UNSURE, you should pass the -e flag
to this script. If you aren't concerned, or you want to create your own
virtualenv environment, then feel free to ignore this message.

VIRTUALENV_WARNING
fi

read -p "Press [Yy] to begin installation with the flag -e $(tput setaf 2)[RECOMMENDED]$(tput sgr 0)
[OR] 
Press [Nn] to continue with the normal installation..." yn
case $yn in 
    [Yy]* ) 
            WITH_VIRTUAL_ENV=1
            ;;
    [Nn]* ) 
            WITH_VIRTUAL_ENV=0 
            ;;
    * ) echo "Please answer yes or no.." ;;
esac

fi

# Find absolute path to the easy-ocw directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

header "Checking for pip ..."
command -v pip >/dev/null 2>&1 || { 
    task "Unable to locate pip."
    task "Installing Pip"
    sudo apt-get install python-pip >> install_log
    subtask "done"
}

if [ $WITH_VIRTUAL_ENV == 1 ]; then
    header "Setting up a virtualenv ..."

    # Check if virtualenv is installed. If it's not, we'll install it for the user.
    command -v virtualenv >/dev/null 2>&1 || { 
        task "Installing virtualenv ..."
        sudo apt-get install -y python-virtualenv >> install_log
        subtask "done"
    }

    # Create a new environment for OCW work
    task "Creating a new environment ..."
    virtualenv venv-ocw >> install_log
    source venv-ocw/bin/activate
    subtask "done"
fi

# Install Continuum Analytics Miniconda Python distribution. This gives
# almost all the dependencies that OCW needs in a single, easy to
# install package.

header "Installing Miniconda Python distribution ..."
echo
echo "*** NOTE *** When asked to update your PATH, you should respond YES and please do not change the default installation directory"
read -p "Press [ENTER] to continue ..."


task "Downloading Miniconda ..."
wget -O Miniconda-latest-linux.sh "https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh" 2>> install_log
subtask "done"

task "Installing ..."
bash Miniconda-latest-linux.sh
subtask "done"

header "Installing dependencies via conda"
task "Reading and installing from ocw-conda-dependencies.txt"
conda install --file ocw-conda-dependencies.txt >> install_log
subtask "done"

# Install miscellaneous Python packages needed for OCW. Some of these
# can be installed with Conda, but since none of them have an annoying
# compiled component we just installed them with Pip.
header "Installing additional Python packages"
task "Reading and installing from ocw-pip-dependencies.txt"
pip install -r ocw-pip-dependencies.txt >> install_log
subtask "done"

header "Installing ocw module"
cd ..
python setup.py install >> install_log
subtask "finished installing ocw module"

header "Installation completed. Please close the terminal and start to new one for the changes to take effect"
header "For any issues with installation please contact dev@climate.apache.org"

