#!/bin/sh
cmd="python /home/selery/tests/random_bibliothecary.py --clonefolder=clone"
echo $cmd
docker run --rm -it \
--env-file ~/.libreselery/tokens.env \
-v ~/db:/home/selery/.libreselery/db libreselery bash \
-c "$cmd" \
