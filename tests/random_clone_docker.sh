#!/bin/sh
cmd="python /home/proton/tests/random_bibliothecary.py --clonefolder=clone"
echo $cmd
docker run --rm -it \
--env-file ~/.protontypes/tokens.env \
-v ~/db:/home/proton/.protontypes/db protontypes bash \
-c "$cmd" \
