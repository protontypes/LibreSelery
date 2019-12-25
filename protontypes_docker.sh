#!/bin/sh
cmd="--folder=$@"
echo $cmd
docker run --rm \
--env-file ~/.protontypes/tokens.env \
-v $@:$@ \
-v ~/.protontypes/db:/home/proton/db \
protontypes \
$cmd \

