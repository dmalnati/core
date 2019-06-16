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
    # Pull in environment varibles

    # declare that any variables we encounter are to be exported
    set -o allexport

    envmapName="$CORE/runtime/working/core_envmap.env"
    if [ ! -f "$envmapName" ]
    then
        $("$CORE/core/scripts/Install.py" -createEnvironmentMap)
    fi

    # source the NAME=VALUE environment variables
     . "$envmapName"

    # no longer auto export
    set +o allexport


    # set up convenience variables
    export CC="$CORE/site-specific/cfg"
    export L="$CORE/runtime/logs"
    export GC="$CORE/generated-cfg"
    
    # set up convenience commands
    alias ss="cd $CC"
    alias l="cd $L"
    alias gc="cd $GC"
    arclog(){ cd "$CORE/archive/`ls $CORE/archive/ | tail -n 1`/logs" ; }
    
    alias c="cd $CORE"
    alias ccf="cd $CORE/core/cfg"
    alias cs="cd $CORE/core/scripts"
    alias ct="cd $CORE/core/test"
    alias cl="cd $CORE/core/lib"
    alias cw="cd $CORE/core/web"
    
    sp(){ StartProcess.py $1 ; }
    st(){ StartProcess.py $1 ; tail -f $L/$1.* ; }
    rt(){ RestartProcess.py $1 ; tail -f $L/$1.* ; }
    kp(){ KillProcess.py $1 ; }
    t(){ tail -f $L/$1.* ; }
    vl(){ vim -R $L/$1.* ; }
    ll(){ less $L/$1.* ; }
    serv(){ testWSAppServer.py $1 ; }
    cli(){ testWSAppClient.py $1 ; }
    
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
    complete -F GetProductListAsTabCompletion  sp
    complete -F GetProductListAsTabCompletion  st
    complete -F GetProductListAsTabCompletion  RestartProcess.py
    complete -F GetProductListAsTabCompletion  rt
    complete -F GetProductListAsTabCompletion  KillProcess.py
    complete -F GetProductListAsTabCompletion  kp
    complete -F GetProductListAsTabCompletion  t
    complete -F GetProductListAsTabCompletion  vl
    complete -F GetProductListAsTabCompletion  ll
    complete -F GetProductListAsTabCompletion  WSReq.py
    complete -F GetProductListAsTabCompletion  testWSAppClient.py
    complete -F GetProductListAsTabCompletion  cli
    complete -F GetProductListAsTabCompletion  testWSAppServer.py
    complete -F GetProductListAsTabCompletion  serv

    # make hitting tab expand variables on command line
    shopt -s direxpand
fi









