#!/bin/bash
# Start command
cmd="python proton.py --folder=$@"

docker run --rm -it \
--env GITHUB_TOKEN=$GITHUB_TOKEN \
--env LIBRARIES_IO_TOKEN=$LIBRARIES_IO_TOKEN \
-v $@:$@ \
-v ~/db:/home/proton/.protontypes/db \
protontypes \
bash -c "$cmd" \
