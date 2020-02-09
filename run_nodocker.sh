#!/bin/bash

#target dir either first argument or the current working directory
if [[ -n $1 ]]; then
  TARGET_DIR=$1
else
  TARGET_DIR=$PWD
fi

env $(cat ~/.openselery/tokens.env) python selery.py --config $TARGET_DIR/selery.yml --directory $TARGET_DIR --result results
