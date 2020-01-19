#!/bin/sh
cmd="python /home/selery/tests/random_bibliothecary.py --clonefolder=clone"
echo $cmd
docker run --rm -it \
--env-file ~/.openselery/tokens.env \
-v ~/db:/home/selery/.openselery/db openselery bash \
-c "$cmd" \
