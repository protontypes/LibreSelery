#!/bin/sh
cmd="python /root/protontypes.py --project $@"
echo $cmd
docker run --rm -it -v $@:$@ protontypes bash -c "$cmd"
