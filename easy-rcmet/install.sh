#!/bin/bash

WITH_VIRTUAL_ENV=0
WITH_INTERACT=1

help()
{
cat << ENDHELP

Easy RCMET assists with the building of the RCMES Toolkit and its dependencies

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
echo "                         Welcome to Easy RCMET"
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

    # Create a new environment for RCMES work
    mkvirtualenv rcmes
    workon rcmes
fi

### Install the latest RCMET code for development!
header "Grabbing RCMET code"
svn co https://svn.apache.org/repos/asf/incubator/climate/trunk/rcmet/src/main/python/rcmes/ src/rcmes

### Build
header "Begin Buildout"
python bootstrap.py -d
./bin/buildout -vvvvv

### Outro
header "Easy RCMET installation complete."

cat << OUTRO
If this installed virtualenv for you, make sure you set the following values in
your shell's RC file.

    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh

Similarly, the default virtualenv environment that this script creates for you
to use during RCMES work is called "rcmes". Whenever you want to work on RCMES
tasks be sure to run

    workon rcmes

This will activate the RCMES environment. When you're done, run

    deactivate rcmes

If you would like to read more about how to use virtualenv and 
virtualenvwrapper please look to the following websites for documentation.

    http://www.virtualenv.org/en/latest/
    http://virtualenvwrapper.readthedocs.org/en/latest/

Additonally, you should set your PYTHON_PATH environment variable to point to the
RCMET code base that was downloaded into ./src/rcmes. For example:
    
    export PYTHON_PATH=/path/to/this/script/src/rcmes:$PYTHON_PATH

OUTRO
