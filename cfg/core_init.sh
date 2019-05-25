#!/bin/bash


#
# bootstraps the setup of a core environment.
# account needs to add these lines to the .bashrc:
#
# export CORE="/home/pi/run"
# source "$CORE/core/cfg/core_init.sh"
#


####################################################
#
# Set up runtime environment variables
#
####################################################

if [ ! -z "$CORE" ]
then
    # prevent repeatedly adding to the PATH if repeatedly invoked
    dir="$CORE/core/scripts"
    [[ ":$PATH:" =~ ":$dir:" ]] || PATH="$dir:$PATH"
    export PATH

    export CC="$CORE/site-specific/cfg"
    export L="$CORE/runtime/logs"
    export GC="$CORE/generated-cfg"
fi









