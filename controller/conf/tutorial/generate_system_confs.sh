#!/bin/bash

# Copyright (C) 2020 Georgia Tech Center for Experimental Research in Computer
# Systems

# Process command-line arguments.
set -u
while [[ $# > 1 ]]; do
  case $1 in
    --cloudlab_profile )
      cloudlab_profile=$2
      ;;
    --cpu )
      cpu=$2
      ;;
    --gb )
      gb=$2
      ;;
    --queue )
      queue=$2
      ;;
    --threads )
      threads=$2
      ;;
    --words )
      words=$2
      ;;
    * )
      echo "Invalid argument: $1"
      exit 1
  esac
  shift
  shift
done

# Set current directory to the directory of this script.
cd "$(dirname "$0")"

# Generate system configuration files.
for c in $cpu; do
  for g in $gb; do
    for q in $queue; do
      for t in $threads; do
        for w in $words; do
          filename="${cloudlab_profile}_${c}CPU_${g}GB_${q}QUEUE_${t}THREADS_${w}WORDS.yml"
          cp ${cloudlab_profile}_TEMPLATE.yml $filename
          sed -i "s/{{CPU}}/${c}/g" $filename
          sed -i "s/{{GB}}/${g}g/g" $filename
          sed -i "s/{{QUEUE}}/${q}/g" $filename
          sed -i "s/{{THREADS}}/${t}/g" $filename
          sed -i "s/{{WORDS}}/${w}/g" $filename
        done
      done
    done
  done
done
