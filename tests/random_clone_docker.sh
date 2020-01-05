#!/bin/sh
cmd="python /home/proton/tests/random_bibliothecary.py --clonefolder=clone"
echo $cmd
docker run --rm -it \
--env-file ~/.OpenCelery/tokens.env \
-v ~/db:/home/proton/.OpenCelery/db OpenCelery bash \
-c "$cmd" \
