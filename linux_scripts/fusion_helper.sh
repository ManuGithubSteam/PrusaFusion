#!/bin/bash

# helper script to get the filename cleaned up with spaces from Fusion360.
# Gets called from the VM, and lets the deamon know that an export took place.

###############

#debug 

echo > "helper started" > /tmp/fusion_helper

## Detects up to 8 spaces in the filename
STLFILE_RAW="$1 $2 $3 $4 $5 $6 $7 $8"
# Removes trailing spaces
STLFILE=$(echo "$STLFILE_RAW" | sed -e 's/[[:space:]]*$//')

# Filter for Filenames with () in them:
STLFILE=$(echo "$STLFILE" | sed -e 's/_..900.._/\(/g')
STLFILE=$(echo "$STLFILE" | sed -e 's/_..901.._/\)/g')


#debug
echo "$STLFILE" >> /tmp/fusion_helper


echo "Sanitized STL: $STLFILE"
#export
echo "$STLFILE" >  /tmp/fusion_new_stl


# Filter umlauts: öäüß
# Wenn im Dateinamen umlaute drin sind.
# 1 ersetzte umlaute durch ?
# 2. rename Dateiname mit Fragezeichen zu richtigem namen
# 3. lösche den falschen dateinamen
cat /tmp/fusion_new_stl | grep ö
oe=$(echo $?)
# 
if [ "$oe" ];  then
   echo Umlaute >> /tmp/fusion_helper
   NEWNAME=$(echo "$STLFILE" | sed 's/ö/\?)/g')
   echo "$NEWNAME" >> /tmp/fusion_helper
 else
   #keine umlaute
   echo not found>> /tmp/fusion_helper
 fi

