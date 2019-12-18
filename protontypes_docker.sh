#!/bin/sh
cmd="python /root/proton.py --folder $@"
echo $cmd
docker run --rm -it --env-file ~/.protontypes/tokens.env -v $@:$@ -v $(pwd)/db:/root/db protontypes bash -c "$cmd"
