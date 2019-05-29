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
        testDir="$dir/test"
        [[ ":$PATH:" =~ ":$testDir:" ]] || PATH="$testDir:$PATH"
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
    
    # set up convenience commands
    alias ss="cd $CC"
    alias l="cd $L"
    alias gc="cd $GC"
    alias arclog="cd $CORE/archive/`ls $CORE/archive/ | tail -n 1`/logs"
    
    alias c="cd $CORE"
    alias ccf="cd $CORE/core/cfg"
    alias cs="cd $CORE/core/scripts"
    alias ct="cd $CORE/core/test"
    alias cl="cd $CORE/core/lib"
    
    st(){ StartProcess.py $1 ; tail -f $L/$1.* ; }
    rt(){ RestartProcess.py $1 ; tail -f $L/$1.* ; }
    kp(){ KillProcess.py $1 ; }
    t(){ tail -f $L/$1.* ; }
    
    # set up other environment variables which get used
    export CORE_SERVICE_NAME=""
    
    # enable tab completion
    GetProductListAsTabCompletion()
    {
        local curr_arg;

        curr_arg=${COMP_WORDS[COMP_CWORD]}
        
        processList=""
        if [ -f $CORE/generated-cfg/ProcessList.txt ]
        then
            processList=$(cat $CORE/generated-cfg/ProcessList.txt)
        fi

        COMPREPLY=( $(compgen -W '$processList' -- $curr_arg ) );
    }
    complete -F GetProductListAsTabCompletion  StartProcess.py
    complete -F GetProductListAsTabCompletion  st
    complete -F GetProductListAsTabCompletion  RestartProcess.py
    complete -F GetProductListAsTabCompletion  rt
    complete -F GetProductListAsTabCompletion  KillProcess.py
    complete -F GetProductListAsTabCompletion  kp
    complete -F GetProductListAsTabCompletion  t
    complete -F GetProductListAsTabCompletion  WSReq.py
    complete -F GetProductListAsTabCompletion  testWSClient.py
    complete -F GetProductListAsTabCompletion  testWSAppClient.py

    # make hitting tab expand variables on command line
    shopt -s direxpand
fi









