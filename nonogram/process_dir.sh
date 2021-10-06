#!/bin/sh

solver=~/bin/nonogram
log_rule_improve=''

if [ -n "$2" ]; then
  if [ "-r" = "$2" ]; then
    log_rule_improve=$2
  else
    solver=$2
  fi
fi

if [ -n "$3" ]; then
  if [ "-r" = "$3" ]; then
    log_rule_improve=$3
  fi
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
    CMD="${solver} ${file} ${log_rule_improve}"
    echo $CMD
    $CMD
done




