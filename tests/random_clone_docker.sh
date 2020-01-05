#!/bin/sh
cmd="python /home/celery/tests/random_bibliothecary.py --clonefolder=clone"
echo $cmd
docker run --rm -it \
--env-file ~/.opencelery/tokens.env \
-v ~/db:/home/celery/.opencelery/db opencelery bash \
-c "$cmd" \
