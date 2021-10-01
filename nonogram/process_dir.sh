#!/bin/sh

solver=~/bin/nonogram

if [ -n "$2" ]; then
  solver=$2
fi

if [ -n "$1" ]; then
  echo "Processing directory: $1"
  process_dir=$1
else
  echo "First parameter not supplied."
  exit
fi

#FILES=`find -L ~/git/nonogram-db -name "*.non"`
FILES=`find -L ${process_dir} -name "*.non"`
for file in $FILES
do
    CMD="${solver} ${file}"
    echo $CMD
    $CMD
done




