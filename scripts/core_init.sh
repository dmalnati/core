#!/bin/bash


#
# bootstraps the setup of a core environment.
# account needs to add these lines to the .bashrc:
#
# export CORE="/home/pi/run"
# source "$CORE/core/scripts/core_init.sh"
#


####################################################
#
# Set up runtime environment variables
#
####################################################

if [ ! -z "$CORE" ]
then
    # get list of product directories, reversed.
    # we're going to peel off front-to-back, so we want the
    # core product to end up last so it's the most preferred in the various
    # lists of paths we're creating
    productDirList=$($CORE/core/scripts/Install.py -getProductDirListReversed)


    # setup PATH to include each scripts dir of each product
    for dir in $productDirList
    do
        scriptDir="$dir/scripts"
        [[ ":$PATH:" =~ ":$scriptDir:" ]] || PATH="$scriptDir:$PATH"
    done
    export PATH


    # setup python library paths
    for dir in $productDirList
    do
        for libDir in $(find "$dir/lib" -type d 2>/dev/null)
        do
            [[ ":$PYTHONPATH:" =~ ":$libDir:" ]] || PYTHONPATH="$libDir:$PYTHONPATH"
        done
    done
    export PYTHONPATH


    # setup config search paths
    # define in reverse priority order so the variable is sorted in
    # priority order
    configDirList="$CORE/generated-cfg $CORE/site-specific/cfg"
    for dir in $configDirList
    do
        [[ ":$CORE_CFG_PATH:" =~ ":$dir:" ]] || CORE_CFG_PATH="$dir:$CORE_CFG_PATH"
    done
    export CORE_CFG_PATH


    # set up convenience variables
    export CC="$CORE/site-specific/cfg"
    export L="$CORE/runtime/logs"
    export GC="$CORE/generated-cfg"

    # make hitting tab expand variables on command line
    shopt -s direxpand
fi









