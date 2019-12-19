#!/bin/sh
cmd="python /home/proton/tests/clone_random.py --clonefolder=clone"
echo $cmd
docker run --rm -it \
--env-file ~/.protontypes/tokens.env \
-v ~/db:/home/proton/db protontypes bash \
-c "$cmd" \
