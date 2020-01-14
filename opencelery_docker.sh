#!/bin/bash
# Start command
cmd="python celery.py --folder=/home/celery/runningrepo/"

docker run --rm \
--env GITHUB_TOKEN=$GITHUB_TOKEN \
--env LIBRARIES_IO_TOKEN=$LIBRARIES_IO_TOKEN \
--env COINBASE_TOKEN=$COINBASE_TOKEN \
--env COINBASE_SECRET=$COINBASE_SECRET \
-v $@:/home/celery/runningrepo/ \
opencelery \
bash -c "$cmd" \

