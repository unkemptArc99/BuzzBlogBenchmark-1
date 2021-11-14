#!/bin/bash

# Copyright (C) 2020 Georgia Tech Center for Experimental Research in Computer
# Systems

# Process command-line arguments.
set -u
while [[ $# > 1 ]]; do
  case $1 in
    --username )
      username=$2
      ;;
    --controller_node )
      controller_node=$2
      ;;
    --loadgen_node )
      loadgen_node=$2
      ;;
    --apigateway_node )
      apigateway_node=$2
      ;;
    --account_service_node )
      account_service_node=$2
      ;;
    --account_database_node )
      account_database_node=$2
      ;;
    --follow_service_node )
      follow_service_node=$2
      ;;
    --like_service_node )
      like_service_node=$2
      ;;
    --post_service_node )
      post_service_node=$2
      ;;
    --post_database_node )
      post_database_node=$2
      ;;
    --uniquepair_service_node )
      uniquepair_service_node=$2
      ;;
    --uniquepair_database_node )
      uniquepair_database_node=$2
      ;;
    * )
      echo "Invalid argument: $1"
      exit 1
  esac
  shift
  shift
done

# Log into controller node.
ssh -o StrictHostKeyChecking=no ${username}@${controller_node} "
  # Clone this repository to get the experiment configuration files.
  ssh-keygen -F github.com || ssh-keyscan github.com >> ~/.ssh/known_hosts
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/conf/tutorial/* .
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark

  # Set up configuration files.
  sed -i \"s/{{username}}/${username}/g\" system.yml
  sed -i \"s/{{loadgen_node}}/${loadgen_node}/g\" system.yml
  sed -i \"s/{{apigateway_node}}/${apigateway_node}/g\" system.yml
  sed -i \"s/{{account_service_node}}/${account_service_node}/g\" system.yml
  sed -i \"s/{{account_database_node}}/${account_database_node}/g\" system.yml
  sed -i \"s/{{follow_service_node}}/${follow_service_node}/g\" system.yml
  sed -i \"s/{{like_service_node}}/${like_service_node}/g\" system.yml
  sed -i \"s/{{post_service_node}}/${post_service_node}/g\" system.yml
  sed -i \"s/{{post_database_node}}/${post_database_node}/g\" system.yml
  sed -i \"s/{{uniquepair_service_node}}/${uniquepair_service_node}/g\" system.yml
  sed -i \"s/{{uniquepair_database_node}}/${uniquepair_database_node}/g\" system.yml
"

ssh -o StrictHostKeyChecking=no ${username}@${loadgen_node} "
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark
"

ssh -o StrictHostKeyChecking=no ${username}@${apigateway_node} "
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark
"

ssh -o StrictHostKeyChecking=no ${username}@${account_service_node} "
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark
"

ssh -o StrictHostKeyChecking=no ${username}@${account_database_node} "
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark
"

ssh -o StrictHostKeyChecking=no ${username}@${follow_service_node} "
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark
"

ssh -o StrictHostKeyChecking=no ${username}@${like_service_node} "
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark
"

ssh -o StrictHostKeyChecking=no ${username}@${post_service_node} "
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark
"

ssh -o StrictHostKeyChecking=no ${username}@${post_database_node} "
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark
"

ssh -o StrictHostKeyChecking=no ${username}@${uniquepair_service_node} "
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark
"

ssh -o StrictHostKeyChecking=no ${username}@${uniquepair_database_node} "
  git clone https://github.com/unkemptArc99/BuzzBlogBenchmark-1.git -b klockstat BuzzBlogBenchmark
  mv BuzzBlogBenchmark/controller/tools/* .
  rm -rf BuzzBlogBenchmark
"