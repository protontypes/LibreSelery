#!/bin/sh
cmd="--folder=$@"
echo $cmd
docker run --rm \
--env GITHUB_TOKEN=$GITHUB_TOKEN --env LIBRARIES_IO_TOKEN=$LIBRARIES_IO_TOKEN \
-v $@:$@ \
-v ~/.protontypes/db:/home/proton/db \
protontypes \
$cmd \

