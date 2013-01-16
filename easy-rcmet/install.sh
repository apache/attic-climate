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

if (($WITH_INTERACT == 1))
then
cat << ENDINTRO
The following packages will be installed:
    List of stuff

It is highly recommended that you allow this script to install and configure a
virtualenv environment for you. If you didn't pass the -e flag when running
this script, you're fine! Otherwise, know what you're doing! Parts of this
script will pollute your global Python install if you don't run within a
virtualenv environment.

ENDINTRO

read -p "Press [ENTER] to being installation..."
fi

### Build
header "Begin Buildout"
python bootstrap.py -d
./bin/buildout

### Cleanup
header "Begin Cleanup"
rm -rf bin/ develop-eggs/ eggs/ parts/

### Outro
header "Easy RCMET installation complete."
