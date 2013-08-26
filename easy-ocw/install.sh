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
#

WITH_VIRTUAL_ENV=0
WITH_INTERACT=1

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
    echo "---------------------------------------------------------------------------" 
    echo "" $1
    echo "---------------------------------------------------------------------------" 
    echo
}

subheader()
{
    echo
    echo ">" $1
    echo
}
    
### Argument Parsing
while getopts "heq" FLAG
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

###
echo
echo "---------------------------------------------------------------------------" 
echo "                         Welcome to Easy OCW"
echo "---------------------------------------------------------------------------" 
echo

if [ $WITH_INTERACT == 1 ]
then
cat << ENDINTRO
The following packages will be installed:
    zlib                curl
    szip                jpeg
    libpng              freetype
    numpy               scipy
    matplotlib          hdf5
    NetCDF              NetCDF4-Python
    NCL                 PyNIO
    PyNGL               Bottle

It is highly recommended that you allow this script to install and configure a
virtualenv environment for you. If you passed the -e flag when running
this script you're fine! Otherwise, know what you're doing! Parts of this
script will pollute your global Python install if you don't run within a
virtualenv environment. If you already have a virtualenv environment into which
you want installs to go then make sure you don't pass -e!

ENDINTRO

read -p "Press [ENTER] to being installation..."
fi

### virtualenv install (if required)
if [ $WITH_VIRTUAL_ENV == 1 ]
then
    if ! command -v pip >/dev/null
    then
        subheader "Installing Pip (and distribute just in case)"
        subheader "Distribute"
        curl http://python-distribute.org/distribute_setup.py | python

        subheader "Pip"
        curl -O http://pypi.python.org/packages/source/p/pip/pip-1.2.1.tar.gz
        tar xzf pip-1.2.1.tar.gz
        cd pip-1.2.1/
        python setup.py install
    fi

    subheader "Installing virtualenv..."
    pip install virtualenv
    subheader "Installing virtualenvwrapper..."
    pip install virtualenvwrapper

    # Need to setup environment for virtualenv
    export WORKON_HOME=$HOME/.virtualenvs
    virtualEnvLoc=`which virtualenv`
    source "${virtualEnvLoc}wrapper.sh"

    # Create a new environment for OCW work
    mkvirtualenv ocw
    workon ocw
fi

### Install the latest OCW code for development!
header "Grabbing OCW code"
svn co https://svn.apache.org/repos/asf/incubator/climate/trunk/rcmet/src/main/python/rcmes/ src/ocw

### Build
header "Begin Buildout"
python bootstrap.py -d
./bin/buildout -vvvvv

### Outro
header "Easy OCW installation complete."

cat << OUTRO
If this installed virtualenv for you, make sure you set the following in
your shell's RC file.

    export WORKON_HOME=$HOME/.virtualenvs

Additionally, you need to source the virtualenvwrapper script in your shell's
RC file. Run the following to find the location of the file.

	which virtualenv

Take the output from the above, add "wrapper.sh" to the end and place it in your
shell's RC file. As an example, if the result of 'which virtualenv' gives you
'/usr/local/bin' then you place the following in your shell's RC file:

    source /usr/local/bin/virtualenvwrapper.sh

If you have a hard time finding the location of the virtualenvwrapper script 
with the above method you can also run the following. Be aware that this could
take a while to finish.

	find / -name "virtualenvwrapper.sh"

The default virtualenv environment that this script creates for you
to use during OCW work is called "ocw". Whenever you want to work on OCW
tasks be sure to run

    workon ocw

This will activate the OCW environment. When you're done, run

    deactivate ocw

If you would like to read more about how to use virtualenv and 
virtualenvwrapper please look to the following websites for documentation.

    http://www.virtualenv.org/en/latest/
    http://virtualenvwrapper.readthedocs.org/en/latest/

Additonally, you should set your PYTHONPATH environment variable to point to the
OCW code base that was downloaded into ./src/ocw For example:
    
    export PYTHONPATH=/path/to/this/script/src/ocw:$PYTHONPATH

OUTRO
