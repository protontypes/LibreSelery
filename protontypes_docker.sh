#!/bin/sh
cmd="python proton.py --folder=$@"
echo $cmd
docker run --rm -it \
--env-file ~/.protontypes/tokens.env \
-v $@:$@ \
-v ~/.protontypes/db:/home/proton/db \
protontypes \
$cmd \

