#!/bin/sh
cmd="python /home/proton/tests/random_bibliothecary.py --clonefolder=clone"
echo $cmd
docker run --rm -it \
--env-file ~/.opencelery/tokens.env \
-v ~/db:/home/proton/.opencelery/db opencelery bash \
-c "$cmd" \
