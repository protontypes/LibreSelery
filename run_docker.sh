#!/bin/sh
cmd="python ./protontypes.py $@"
echo $cmd
docker run --rm -it -v $(pwd):/root protontypes bash -c "$cmd"
