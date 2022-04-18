# Copyright (C) 2020 Georgia Tech Center for Experimental Research in Computer
# Systems

# Define base configuration.
FROM python:3.9-buster
MAINTAINER ral@gatech.edu
WORKDIR /usr/local/

# Declare environment variables.
ENV hostname null
ENV port null
ENV seed null

# Install ATLoad v0.1.
RUN cd lib \
  && wget https://github.com/rodrigoalveslima/ATLoad/archive/v0.1.tar.gz \
  && tar -xzf v0.1.tar.gz \
  && rm v0.1.tar.gz

# Build directory tree and copy files.
RUN mkdir -p src/loadgen
COPY loadgen.py src/loadgen
COPY requirements.txt src/loadgen

# Install Python dependencies.
RUN pip install --no-cache-dir -r src/loadgen/requirements.txt
RUN pip install --no-cache-dir -r lib/ATLoad-0.1/requirements.txt

# Start the workload generator.
CMD ["/bin/bash", "-c", "PYTHONPATH=/usr/local/lib/ATLoad-0.1/src python3 src/loadgen/loadgen.py --workload_conf etc/loadgen/workload.yml --log /tmp/loadgen.log --hostname $hostname --port $port --seed $seed"]
