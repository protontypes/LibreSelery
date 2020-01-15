#!/bin/bash
# Never print SECRET or TOKENS.

# Mount the argument folder into the container \
docker run --rm \
--env GITHUB_TOKEN=$GITHUB_TOKEN \
--env LIBRARIES_IO_TOKEN=$LIBRARIES_IO_TOKEN \
--env COINBASE_TOKEN=$COINBASE_TOKEN \
--env COINBASE_SECRET=$COINBASE_SECRET \
-v $@:/home/celery/runningrepo/ \
opencelery \
bash -c "python celery.py --folder=/home/celery/runningrepo/" \

