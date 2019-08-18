#!/bin/bash

# helper script to get the filename cleaned up with spaces from Fusion360.
# Gets called from the VM, and lets the deamon know that an export took place.

###############
## Detects up to 8 spaces in the filename
STLFILE_RAW="$1 $2 $3 $4 $5 $6 $7 $8"
STLFILE=$(echo $STLFILE_RAW | sed -e 's/[[:space:]]*$//')

echo "Sanitized STL: $STLFILE"
echo "$STLFILE" >  /tmp/fusion_new_stl



