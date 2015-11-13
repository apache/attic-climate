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

export ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future

help()
{
cat << ENDHELP

Easy OCW assists with the building of the Apache Open Climate Workbench and its dependencies

Flags:
    -h  Display this help message.
    -e  Install and configure a virtualenv environment before installation.
    -q  Quiet install. User prompts are removed (when possible).

It is recommended that you pass -e when running this script. If you don't, parts
of this installation will pollute your global Python install. If you're unsure,
pass -e just to be safe!

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
INIT_PWD=$PWD

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
$(tput setaf 1)<-----------------------------[WARNING!]-----------------------------------> 
It is highly recommended that you allow Easy OCW to install the dependencies
into a virtualenv environment to ensure that your global Python install is
not affected. If you're UNSURE, you should pass the -e flag
to this script. If you aren't concerned, or you want to create your own
<<<<<<< HEAD
virtualenv environment, then feel free to ignore this message.$(tput sgr 0)
=======
virtualenv environment, then feel free to ignore this message.$(tput setaf 0)
>>>>>>> 328cb6e193b5dd3e5f30acb421a31d4ac26ea397

VIRTUALENV_WARNING
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

else 
    read -p "Press [Enter] to continue..."

fi

<<<<<<< HEAD
=======
read -p "Press [Yy] to begin installation with the flag -e $(tput setaf 2)[RECOMMENDED]$(tput setaf 0)
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
>>>>>>> 328cb6e193b5dd3e5f30acb421a31d4ac26ea397
fi

header "Checking for pip ..."
command -v pip >/dev/null 2>&1 || { 
    task "Unable to locate pip."
    task "Installing Distribute"
    curl http://python-distribute.org/distribute_setup.py | python >> install_log
    subtask "done"

    task "Installing Pip"
    curl -O http://pypi.python.org/packages/source/p/pip/pip-1.2.1.tar.gz >> install_log
    tar xzf pip-1.2.1.tar.gz >> install_log
    cd pip-1.2.1/
    python setup.py install >> install_log
    subtask "done"
}

if [ $WITH_VIRTUAL_ENV == 1 ]; then
    header "Setting up a virtualenv ..."

    # Check if virtualenv is installed. If it's not, we'll install it for the user.
    command -v virtualenv >/dev/null 2>&1 || { 
        task "Installing virtualenv ..."
        pip install virtualenv >> install_log
        subtask "done"
    }

    read -e -p "Enter the path where you want to install the ocw virtual environment..." ocw_path 

    header "Checking for previously installed  ocw virtual environment..."
    cd $ocw_path

    if [ -e $ocw_path/ocw/bin/python ]; then
        echo "We found an existing 'ocw' virtualenv on your system in ~/ocw."
        read -n1 -p "Do you want to replace it with a clean install? y/n :" replace 
        if [ "$replace" == "y" ]; then
            echo ""
            echo "$(tput setaf 1)[WARNING!] This will delete all file and data in ~/ocw on your system.$(tput sgr 0)"
            read -n1 -p "To confirm and proceed type y or press ENTER to quit:" confirm
            if [ "$confirm" == "y" ]; then
                echo ""
                echo "Deleting contents of ~/ocw" 
                rm -rf $ocw_path/ocw/bin/python >> install_log
            else
                echo ""
                echo "Stopping Open Climate Workbench Installation"
                exit
            fi
        else
            echo ""
            echo "Stopping Open Climate Workbench Installation because an existing 'ocw'"
            echo "virtual environment already exists."
            exit
        fi
    fi


    #check if the file path exists.
    while [ ! -d "$ocw_path" ];
    do 
        echo "Path not found..."
        read -e -p "Please enter a valid path..." ocw_path
    done 

    # Create a new environment for OCW work
    task "Creating a new environment in ~/ocw..."
    virtualenv ocw >> install_log
    source ~/ocw/bin/activate >> install_log
    cd $INIT_PWD
    subtask "done"
fi

header "Installing conda for package management ..."

pip install conda >> install_log
conda init >> install_log


header "Installing dependencies with conda ..."
echo | conda install --file ocw-conda-dependencies.txt

# We only use conda for the annoying dependencies like numpy,
# scipy, matplotlib, and basemap. For everything else, we stick
# with pip.
header "Installing additional Python packages"
pip install -r ocw-pip-dependencies.txt >> install_log

if [ $WITH_VIRTUAL_ENV == 1 ]; then
    echo "***POST INSTALLATION NOTE***

If you are familiar with virtualenv you should know that activating
the new 'ocw' environment is different because we use conda to install
packages.  An example of the command you want to run is listed in the
alias below.

To make it easier to change into the 'ocw' virtualenv add the
following alias to your ~/.bash_profile

    alias ocw='source ~/ocw/bin/activate ~/ocw/'

When you want to use ocw in the future, you just have to type 'ocw'
in your terminal."
else
    echo "***POST INSTALLATION NOTE***

If you have run this script within your own virtualenv you need to know
a couple of caveats/side effects that are caused by using conda to install
packages within the virtualenv.

- Virtualenv wrapper will throw errors like those outlined here:
https://issues.apache.org/jira/browse/CLIMATE-451

- You will not be able to 'activate' the environment using the normal
virtualenv command, you must instead use the conda activate command as follows:

source path/to/your_env/bin/activate path/to/your_env

Example:  (assuming your env is in ~/.virtualenv/ocw)

source ~/.virtualenv/ocw/bin/activate ~/.virtualenv/ocw

"

fi

