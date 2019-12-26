#!/bin/sh
cmd="python proton.py --folder=$@"
echo $cmd
docker run --rm -it \
--env-file ~/.protontypes/tokens.env \
=======
cmd="--folder=$@"
echo $cmd
docker run --rm \
--env GITHUB_TOKEN=$GITHUB_TOKEN i \
--env LIBRARIES_IO_TOKEN=$LIBRARIES_IO_TOKEN \

-v $@:$@ \
-v ~/.protontypes/db:/home/proton/db \
protontypes \
$cmd \

