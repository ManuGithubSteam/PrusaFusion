#!/bin/bash

# helper script to get the filename cleaned up with spaces from Fusion360.
# Gets called from the VM, and lets the deamon know that an export took place.

###############

#debug 

echo "helper started" > /tmp/fusion_helper

## Detects up to 9 spaces in the filename
STLFILE_RAW="$1 $2 $3 $4 $5 $6 $7 $8 $9 "
# Removes trailing spaces
STLFILE=$(echo "$STLFILE_RAW" | sed -e 's/[[:space:]]*$//')

# Convert from Windows file encoding to Linux
convmv -f iso-8859-15 -t UTF-8 --nosmart --notest /tmp/*.stl

# Filter for Filenames with () in them:
STLFILE=$(echo "$STLFILE" | sed -e 's/_..900.._/\(/g')
STLFILE=$(echo "$STLFILE" | sed -e 's/_..901.._/\)/g')

echo "Sanitized STL: $STLFILE"
#export
echo "$STLFILE" >  /tmp/fusion_new_stl_win

iconv -f iso-8859-15 -t UTF-8 /tmp/fusion_new_stl_win > /tmp/fusion_new_stl
#cleanup
rm /tmp/fusion_new_stl_win

