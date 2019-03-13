#!/bin/sh
# \
exec tclsh "$0" "$@"


set FIRST_TIME   1
set COL_LIST { C1.mV C1.mA C2.mV C2.mA C3.mV C3.mA }
array set COL__IDX [list]
set LINE_PART_LIST_LAST [list]



proc ClearScreen { } {
    exec clear >@ stdout
}

proc MoveCursorToUpperLeft { } {
    puts -nonewline "\x1b\[0;0f"
}


proc CommaSplitAndTrim { str } {
    return [join [split $str ","] " "]
}



#
# Processes a given line looking for headers.
#
# return 1 if caller can process this line themselves knowing that the
# indexes are in a good state
#
# return 0 if the caller cannot process this line
proc CanProcessLine { linePartList } {
    global COL__IDX
    global COL_LIST
    global LINE_PART_LIST_LAST

    set retVal 1

    set colFirst    [lindex $COL_LIST 0]
    set idxColFirst [lsearch -exact $linePartList $colFirst]

    if { $idxColFirst != -1 } {
        # Found a header line, so definitely caller shouldn't process it
        set retVal 0

        foreach { col } $COL_LIST {
            set idx [lsearch -exact $linePartList $col]

            if { $idx != -1 } {
                set COL__IDX($col) $idx
            } else {
                puts "Couldn't find $col in a header row, exiting"
                exit -1
            }
        }
    } else {
        # Not a header

        # but have we seen a header before that we can use?
        # if we have indexes for any column, then yes, otherwise no
        foreach { col } $COL_LIST {
            if { [info exists COL__IDX($col)] } {
                set retVal 1
            }
        }
    }

    # also check that the number of columns exceeds the minimum to avoid
    # processing the garbage I type in or other status messages
    if { [llength $linePartList] < [llength $COL_LIST] } {
        set retVal 0
    }

    # double-check that by filtering lines which start with \[
    if { [string index [lindex $linePartList 0] 0] == "\[" } {
        set retVal 0
    }

    set LINE_PART_LIST_LAST $linePartList

    return $retVal
}

proc Get { col } {
    global COL__IDX
    global LINE_PART_LIST_LAST

    set retVal 0
    if { [info exists COL__IDX($col)] } {
        set idx $COL__IDX($col)

        set retVal [lindex $LINE_PART_LIST_LAST $idx]
    }

    return $retVal;
}


set MV_LIST [list]
array set MV__MW_DATA [list]
proc OnReading { ch mW mV mA } {
    global MV_LIST
    global MV__MW_DATA

    if { $ch == "C1" && $mW != 0 } {
        # truncate mV to buckets of 50
        set bucketSize 50
        set mV [expr int($mV/$bucketSize) * $bucketSize]

        if { ![info exists MV__MW_DATA($mV)] } {
            set MV__MW_DATA($mV) [list 0 0]

            lappend MV_LIST $mV

            set MV_LIST [lsort -dictionary $MV_LIST]
        }

        set data $MV__MW_DATA($mV)

        foreach { mWsum count } $data {
            set mWsum [expr $mWsum + $mW]
            incr count

            set MV__MW_DATA($mV) [list $mWsum $count]
        }
    }
}

proc PrintMPPData { } {
    global MV_LIST
    global MV__MW_DATA

    foreach { mV } $MV_LIST {
        foreach { mW count } $MV__MW_DATA($mV) {
            set avg [expr int($mW / $count)]
            puts [format "%5s , %s                                 " $mV $avg]
        }
    }
}


proc OnLinePartList { linePartList } {
    global FIRST_TIME
    global COL_LIST

    if { $FIRST_TIME } {
        set FIRST_TIME 0

        ClearScreen
    }

    if { [CanProcessLine $linePartList] } {
        MoveCursorToUpperLeft

        foreach { ch } [list C1 C2 C3] {
            set mV [Get $ch.mV]
            set mA [Get $ch.mA]

            set mW [expr int(double($mV)/1000 * double($mA)/1000 * 1000)]

            OnReading $ch $mW $mV $mA

            puts [format "$ch  %-12s %-12s %-12s" \
                  [format "mW=%s" $mW] \
                  [format "mV=%s" $mV] \
                  [format "mA=%s" $mA]]
        }

        puts ""

        PrintMPPData
    }
}

proc Monitor { inFile } {
    set fd stdin
    if { $inFile != "-" } {
        set fd [open $inFile "r"]
    }

    set line [gets $fd]
    while { ![eof $fd] } {
        OnLinePartList [CommaSplitAndTrim $line]

        set line [gets $fd]
    }

    if { $inFile != "-" } {
        close $fd
    }
}

proc Main { } {
    global argc
    global argv
    global argv0

    if { $argc != 1 } {
        puts "Usage: $argv0 <file> (file can be -)"
        exit -1
    }

    set inFile [lindex $argv 0]

    ClearScreen
    Monitor $inFile
}

Main

