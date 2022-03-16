# Tutorial
This tutorial shows how to run a systems performance experiment in CloudLab
using the BuzzBlog Benchmark.

If you are a Georgia Tech student enrolled in the courses *Introduction to
Enterprise Computing* (CS4365/6365) or *Real-Time/Embedded Systems*
(CS4220/CS6235), read the [tutorial on how to setup a CloudLab
account](CLOUDLAB.md) first.

## Cloud Instantiation
1. Access the [CloudLab login page](https://cloudlab.us/login.php) and sign in.
2. In the main menu, click on [Start Experiment](https://www.cloudlab.us/instantiate.php).
3. Click on *Change Profile*.
4. Search profile *BuzzBlog-19_xl170_nodes* of project *Infosphere*. This
profile contains the specification of a cloud comprising 19 xl170 machines (x86)
connected to a LAN and running a patched version of Ubuntu 20.04 LTS (focal) 64-bit. Click
on *Select Profile*.
5. Optionally, you can give a name to your experiment. Click on *Next*.
6. Optionally, you can set a start time and duration for your experiment. Clouds
last for 16 hours by default, but you will need much less time to run your
experiment. Be courteous and set a smaller value for the experiment duration.
Also, please immediately terminate it after you are done.
7. Click on *Finish*.

Your cloud will be ready in approximately 10 minutes, if the requested resources
are available.

## Controller Setup
The experiment workflow is executed by the `controller`, a containerized
application that installs software dependencies in the nodes, deploys services,
starts monitors and tracers, runs the workload generator, and finally collects
the resulting log, monitoring, and tracing files.

To setup `node-0` for running `controller`:
1. Download `scripts/controller_setup.sh` to your local machine.
2. Run the script:
```
chmod +x controller_setup.sh
./controller_setup.sh \
    --username [your cloudlab username] \
    --private_ssh_key_path [path to your private ssh key] \
    --controller_node [node-0 hostname]
```

`controller_setup.sh` will copy your SSH private key to `node-0` so the
`controller` can access other nodes. This SSH private key must be the one
associated with the SSH public key that you uploaded to CloudLab when creating
your account. For security reasons, use this SSH key pair for your CloudLab
experiments only. This script will also install the software dependencies needed
for running the `controller`.

## Experiment Configuration
To generate the experiment configuration files in `node-0`:
1. Download `scripts/tutorial_configuration_setup.sh` to your local machine.
2. Run the script:
```
chmod +x tutorial_configuration_setup.sh
./tutorial_configuration_setup.sh \
    --username [your cloudlab username] \
    --controller_node [node-0 hostname] \
    --system_template BuzzBlog-19_xl170_nodes.yml
    --workload_template BuzzBlog-read_intensive_workload.yml
```

In this example, we use the system configuration specified in the file
`controller/conf/tutorial/BuzzBlog-19_xl170_nodes.yml`.

Log into `node-0`.
```
ssh [your cloudlab username]@[node-0 hostname]
```

In the home folder, you will find the experiment configuration files
`system.yml` and `workload.yml`.

### System Configuration
File `system.yml` contains the system configuration of each node. In this file,
it is possible to specify the kernel parameters to be overwritten, the
containers to be deployed and their options, the monitors and tracers to be
started and their options, and the variables to render configuration files
needed by containers deployed in each node.

For a better understanding of your experiment, check this system configuration
file and how it is used by the `controller` (specifically, in the Python program
`controller/src/run_experiment.py`) to execute the experiment workflow.

### Workload Configuration
File `workload.yml` contains the workload configuration. It defines the number
of clients to be simulated, the average number of requests to be made per second
(throughput), the periods with increased throughput (surges), and the
probabilities of transitioning between request types.

For a better understanding of your experiment, check this workload configuration
file and how it is used by `loadgen` (specifically, in the Python program
`loadgen/loadgen.py`) to generate requests simulating user interactions with the
BuzzBlog application.

## Experiment Execution
Still in `node-0`, run (Docker Hub credentials are optional parameters):
```
sudo docker run \
    --env description="My first BuzzBlog experiment." \
    --env docker_hub_username="" \
    --env docker_hub_password="" \
    --volume $(pwd):/usr/local/etc/BuzzBlogBenchmark \
    --volume $(pwd):/var/log/BuzzBlogBenchmark \
    --volume $(pwd)/.ssh:/home/$(whoami)/.ssh \
    $(echo $(cat /etc/hosts | grep node- | sed 's/[[:space:]]/ /g' | cut -d ' ' -f 1,4 | sed 's:^\(.*\) \(.*\):\2\:\1:' | awk '{print "--add-host="$1""}')) \
    rodrigoalveslima/buzzblog:benchmarkcontroller_v0.1
```

This experiment will take approximately 75 minutes to finish. The results will
be in a directory named `BuzzBlogBenchmark_[%Y-%m-%d-%H-%M-%S]` located in the
home directory.

After the experiment is complete, compress that directory:
```
tar -czf $(ls . | grep BuzzBlogBenchmark_).tar.gz BuzzBlogBenchmark_*/*
```

Finally, save the experiment results. In your local machine, run:
```
scp [your cloudlab username]@[node-0 hostname]:BuzzBlogBenchmark_*.tar.gz .
```

After copying these results to your local machine, please terminate your cloud
in CloudLab.
