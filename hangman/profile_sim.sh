#!/usr/bin/sh
python -m cProfile hangman_sim.py -l $1 > ./tmp/profile_result_$1.txt 