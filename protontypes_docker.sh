#!/bin/bash
# Start command
cmd="python proton.py --folder=$@"

docker run --rm \
--env GITHUB_TOKEN=$GITHUB_TOKEN \
--env LIBRARIES_IO_TOKEN=$LIBRARIES_IO_TOKEN \
protontypes \
bash -c "$cmd" \
