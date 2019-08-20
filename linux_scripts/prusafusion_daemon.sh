#!/bin/bash

PRUSA_PATH="/home/manuel/.PrusaSlicer/PrusaSlicer-2.0.0+linux64-201905201652.appimage"

##########################

while [ 1 ]
do

if [ -f "/tmp/fusion_new_stl" ]; then
    echo "new fusion export exist"
    STLFILE=$(cat /tmp/fusion_new_stl | head -n 1)
    echo "$STLFILE"
    # lets do it start slicer
    rm /tmp/fusion_new_stl
    
    $PRUSA_PATH /tmp/"$STLFILE"
    
    #cleanup
    rm /tmp/*.stl
fi


sleep 0.2

done
