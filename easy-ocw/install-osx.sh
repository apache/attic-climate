#!/bin/bash
#
# PUT HEADER HERE

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
situation.

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
fi

header "Checking for pip ..."
if [ ! command -v pip >/dev/null 2>&1 ]; then
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
fi

if [ $WITH_VIRTUAL_ENV == 1 ]; then
    header "Setting up a virtualenv ..."

    # Check if virtualenv is installed. If it's not, we'll install it for the user.
    if ! command -v virtualenv >/dev/null 2>&1; then
        task "Installing virtualenv ..."
        pip install virtualenv >> install_log
        subtask "done"
    fi

    # Check if virtualenvwrapper is installed or not. If it's not, we'll
    # install it for the user. Why wouldn't you want to use virtualenvwrapper?!?!
    # It's super awesome! By default, virtualenvwrapper installs to the same place
    # as virtualenv so we'll look for the necessary scripts there. This is fairly
    # brittle, but it should be sufficient for the majority of cases.
    virtualEnvLoc=`which virtualenv`
    virtualEnvWrapperLoc="${virtualEnvLoc}wrapper.sh"

    if [ ! -f $virtualEnvWrapperLoc ]; then
        task "Installing virtualenvwrapper ..."
        pip install virtualenvwrapper >> install_log
        subtask "done"

        task "Setting/sourcing necessary virtualenv things ..."
        # Need to setup environment for virtualenv
        export WORKON_HOME=$HOME/.virtualenvs
        subtask "done"
    fi

    # Just to be safe, we'll source virtualenvwrapper. This is really only
    # necessary if we installed it for the user.
    source $virtualEnvWrapperLoc

    # Create a new environment for OCW work
    task "Creating a new environment ..."
    mkvirtualenv ocw >> install_log
    workon ocw >> install_log
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
task "Installing requests ..."
pip install requests >> install_log
subtask "done"

task "Installing bottle ..."
pip install bottle >> install_log
subtask "done"

task "Installing pydap ..."
pip install pydap >> install_log
subtask "done"

task "Installing webtest ..."
pip install webtest >> install_log
subtask "done"

task "Installing nose ..."
pip install nose >> install_log
subtask "done"

task "Installing pylint ..."
pip install pylint >> install_log
subtask "done"
