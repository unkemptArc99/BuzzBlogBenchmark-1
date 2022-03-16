# Copyright (C) 2020 Georgia Tech Center for Experimental Research in Computer
# Systems

import argparse
import datetime
import os
import re
import subprocess
import threading
import time

import jinja2
import yaml

from ssh_client import SSHClient


### Global variables

DOCKER_HUB_USERNAME = ""
DOCKER_HUB_PASSWORD = ""
DIRNAME = ""
METADATA = {}
SYS_CONF = {}
WL_CONF = {}
BACKEND_CONF = {}
PARSE_LOG_FILES = None


### Utilities

LOG_FILENAME_TO_PARSER = {
  "loadgen.log": "/opt/BuzzBlogBenchmark/analysis/parsers/loadgen_parser.py",
  "queries.log": "/opt/BuzzBlogBenchmark/analysis/parsers/query_parser.py",
  "redis.log": "/opt/BuzzBlogBenchmark/analysis/parsers/redis_parser.py",
  "calls.log": "/opt/BuzzBlogBenchmark/analysis/parsers/rpc_parser.py",
}


def timestamp():
  return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def update_metadata(metadata):
  global METADATA
  METADATA.update(metadata)
  with open(os.path.join(DIRNAME, "metadata.yml"), 'w') as metadata_file:
    metadata_file.write(yaml.dump(METADATA))


def start_container(node_hostname, node_conf, container_name, ssh_client):
  container_conf = node_conf["containers"][container_name]
  ssh_client.exec("sudo docker run " +
      " ".join(["--%s %s" % (param, value) if isinstance(value, str) else
          " ".join(["--%s %s" % (param, v) for v in value])
          for (param, value) in container_conf.get("options", {}).items()]) +
      " " +
      """$(echo $(cat /etc/hosts | grep node- | sed 's/[[:space:]]/ /g' | cut -d ' ' -f 1,4 | sed 's:^\(.*\) \(.*\):\\2\:\\1:' | awk '{print "--add-host="$1""}'))""" +
      " " +
      container_conf["image"])
  time.sleep(16)
  if container_conf["image"].startswith("postgres"):
    # Setup the database.
    subprocess.run("psql -U postgres -d %s -h %s -p %s -f %s" % (
        container_name.split('_')[0],
        node_hostname,
        container_conf["options"]["publish"].split(':')[0],
        "/opt/BuzzBlog/app/{service}/database/{service}_schema.sql".\
            format(service=container_name.split('_')[0])), shell=True)


def count_containers(container_name_pat):
  """Count number of instances of the specified container (regex supported)."""
  count = 0
  for _, node_conf in SYS_CONF.items():
    for container_name in node_conf.get("containers", {}):
      if re.match(container_name_pat, container_name):
        count += 1
  return count


def all_nodes(func):
  """Run func for all nodes in parallel."""
  def func_wrapper(*args, **kwargs):
    threads = []
    for node_hostname, node_conf in SYS_CONF.items():
      ssh_client = SSHClient(node_hostname, node_conf["ssh"]["port"],
          node_conf["ssh"]["username"], node_conf["ssh"]["key_filename"],
          os.path.join(DIRNAME, "ssh",
          "%s-%s" % (node_hostname, func.__name__)))
      threads.append(threading.Thread(target=func,
          args=[node_hostname, node_conf, ssh_client]))
    for thread in threads:
      thread.start()
    for thread in threads:
      thread.join()
  return func_wrapper


def nodes_with_container(container_name_pat):
  """Run func for nodes with the specified container (regex supported)."""
  def func_wrapper_outer(func):
    def func_wrapper_inner(*args, **kwargs):
      threads = []
      for node_hostname, node_conf in SYS_CONF.items():
        for container_name in node_conf.get("containers", {}):
          if re.match(container_name_pat, container_name):
            break
        else:
          continue
        ssh_client = SSHClient(node_hostname, node_conf["ssh"]["port"],
            node_conf["ssh"]["username"], node_conf["ssh"]["key_filename"],
            os.path.join(DIRNAME, "ssh",
            "%s-%s" % (node_hostname, func.__name__)))
        threads.append(threading.Thread(target=func,
            args=[node_hostname, node_conf, ssh_client]))
      for thread in threads:
        thread.start()
      for thread in threads:
        thread.join()
    return func_wrapper_inner
  return func_wrapper_outer


def nodes_with_monitor(monitor_name_pat):
  """Run func for nodes with the specified monitor (regex supported)."""
  def func_wrapper_outer(func):
    def func_wrapper_inner(*args, **kwargs):
      threads = []
      for node_hostname, node_conf in SYS_CONF.items():
        for monitor_name in node_conf.get("monitors", {}):
          if re.match(monitor_name_pat, monitor_name):
            break
        else:
          continue
        ssh_client = SSHClient(node_hostname, node_conf["ssh"]["port"],
            node_conf["ssh"]["username"], node_conf["ssh"]["key_filename"],
            os.path.join(DIRNAME, "ssh",
            "%s-%s" % (node_hostname, func.__name__)))
        threads.append(threading.Thread(target=func,
            args=[node_hostname, node_conf, ssh_client]))
      for thread in threads:
        thread.start()
      for thread in threads:
        thread.join()
    return func_wrapper_inner
  return func_wrapper_outer


### Workflow

@all_nodes
def configure_kernel(node_hostname, node_conf, ssh_client):
  ssh_client.exec(" && ".join(["sudo sysctl -w %s=\"%s\"" % (param, value)
      for param, value in node_conf.get("kernel", {}).items()]))


@all_nodes
def get_system_specs(node_hostname, node_conf, ssh_client):
  with open(os.path.join(DIRNAME, "specs", node_hostname, "hw"), "wb+") as \
      hw_file:
    hw_file.write(ssh_client.exec("sudo lshw")[0])
  with open(os.path.join(DIRNAME, "specs", node_hostname, "cpu"), "wb+") as \
      cpu_file:
    cpu_file.write(ssh_client.exec("lscpu")[0])
  with open(os.path.join(DIRNAME, "specs", node_hostname, "mem"), "wb+") as \
      mem_file:
    mem_file.write(ssh_client.exec("lsmem")[0])
  with open(os.path.join(DIRNAME, "specs", node_hostname, "blk"), "wb+") as \
      blk_file:
    blk_file.write(ssh_client.exec("lsblk")[0])
  with open(os.path.join(DIRNAME, "specs", node_hostname, "kernel"), "wb+") as \
      kernel_file:
    kernel_file.write(ssh_client.exec("sudo sysctl -a")[0])


@nodes_with_container(".+")
def install_buzzblogbenchmark(node_hostname, node_conf, ssh_client):
  VERSION = "0.1"
  ssh_client.exec(
      "sudo mkdir -p /opt/BuzzBlogBenchmark && "
      "sudo curl "
          "https://codeload.github.com/rodrigoalveslima/BuzzBlogBenchmark/tar.gz/refs/tags/v{VERSION} "
          "--output /opt/BuzzBlogBenchmark/v{VERSION}.tar.gz && "
      "sudo tar -C /opt/BuzzBlogBenchmark -xzf /opt/BuzzBlogBenchmark/v{VERSION}.tar.gz && "
      "sudo mv /opt/BuzzBlogBenchmark/BuzzBlogBenchmark-{VERSION}/* /opt/BuzzBlogBenchmark && "
      "sudo rm -rf /opt/BuzzBlogBenchmark/BuzzBlogBenchmark-{VERSION}".format(VERSION=VERSION))


@nodes_with_container(".+")
def install_docker(node_hostname, node_conf, ssh_client):
  ssh_client.exec(
      "sudo apt-get update && "
      "sudo DEBIAN_FRONTEND=noninteractive apt-get -y install "
          "apt-transport-https ca-certificates curl gnupg-agent "
          "software-properties-common && "
      "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | "
          "sudo apt-key add - && "
      "sudo add-apt-repository "
          "\"deb [arch=amd64] https://download.docker.com/linux/ubuntu "
          "$(lsb_release -cs) stable\" && "
      "sudo apt-get update && "
      "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "
          "docker-ce docker-ce-cli containerd.io")


@nodes_with_container(".+")
def install_pandas(node_hostname, node_conf, ssh_client):
  ssh_client.exec(
      "sudo apt-get update && "
      "sudo DEBIAN_FRONTEND=noninteractive apt-get -y install "
          "python3-pip && "
      "pip3 install pandas==1.3.3")


@nodes_with_monitor(".+-bpfcc")
def install_bpfcc(node_hostname, node_conf, ssh_client):
  ssh_client.exec(
      "sudo apt-get update && "
      "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "
          "bpfcc-tools linux-headers-5.4.0-100-generic")


@nodes_with_monitor("collectl")
def install_collectl(node_hostname, node_conf, ssh_client):
  ssh_client.exec(
      "sudo apt-get update && "
      "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y collectl")


@nodes_with_monitor("radvisor")
def install_radvisor(node_hostname, node_conf, ssh_client):
  # Note: we specify to only compile the Docker feature, which disables
  # compiling Kubernetes support via conditional compilation.
  VERSION = "1.3.1"
  ssh_client.exec(
      "sudo apt-get update && "
      "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y rustc cargo && "
      "sudo mkdir -p /opt/radvisor && "
      "sudo curl "
          "https://codeload.github.com/elba-docker/radvisor/tar.gz/v{VERSION} "
          "--output /opt/radvisor/v{VERSION}.tar.gz && "
      "sudo tar -C /opt/radvisor -xzf /opt/radvisor/v{VERSION}.tar.gz && "
      "sudo make -C /opt/radvisor/radvisor-{VERSION} compile "
          "OUT_DIR=/opt/radvisor FEATURES=docker && "
      "sudo cp /opt/radvisor/radvisor /usr/bin/".format(VERSION=VERSION))


@nodes_with_container(".+")
def pull_docker_images(node_hostname, node_conf, ssh_client):
  if DOCKER_HUB_USERNAME and DOCKER_HUB_PASSWORD:
    ssh_client.exec("sudo docker login -u {username} -p {password}".format(
        username=DOCKER_HUB_USERNAME, password=DOCKER_HUB_PASSWORD))
  threads = []
  for container_conf in node_conf.get("containers", {}).values():
    threads.append(threading.Thread(target=ssh_client.exec,
        args=["sudo docker pull %s" % container_conf["image"].split(' ')[0]]))
  for thread in threads:
    thread.start()
  for thread in threads:
    thread.join()


@nodes_with_container("loadgen.*")
def copy_workload_configuration_file(node_hostname, node_conf, ssh_client):
  if WL_CONF:
    ssh_client.exec(
        "sudo mkdir -p /usr/local/etc/loadgen && "
        "echo \"{content}\" | sudo tee {filepath}".format(
            content=yaml.dump(WL_CONF),
            filepath="/usr/local/etc/loadgen/workload.yml"))


@all_nodes
def render_configuration_templates(node_hostname, node_conf, ssh_client):
  env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(
      os.path.dirname(os.path.realpath(__file__)), "templates")))
  for template_name, template_conf in node_conf.get("templates", {}).items():
    if os.path.split(template_conf["output"])[0]:
      ssh_client.exec("sudo mkdir -p %s" % os.path.split(template_conf["output"])[0])
    ssh_client.exec("echo \"{content}\" | sudo tee {filepath}".format(
        content=env.get_template(template_name).\
            render(**template_conf["params"]).replace('"', '\\"'),
        filepath=template_conf["output"]))


@all_nodes
def generate_backend_configuration_file(node_hostname, node_conf, ssh_client):
  ssh_client.exec(
      "sudo mkdir -p /etc/opt/BuzzBlog && "
      "echo \"{content}\" | sudo tee {filepath}".format(
          content=yaml.dump(BACKEND_CONF),
          filepath="/etc/opt/BuzzBlog/backend.yml"))


@nodes_with_monitor(".+")
def start_monitors(node_hostname, node_conf, ssh_client):
  for monitor_name, monitor_conf in node_conf["monitors"].items():
    ssh_client.exec("mkdir -p %s" % monitor_conf["dirpath"])
    ssh_client.exec("sudo nohup nice -n %s " %
        monitor_conf.get("niceness", 19) +
        "stdbuf -oL -eL " +
        monitor_conf.get("command", monitor_name) + " " +
        " ".join(["--%s %s" % (param, value) for (param, value) in
            monitor_conf.get("options", {}).items()]) + " " +
        "> {log} 2>&1 < /dev/null &".format(
            log=monitor_conf.get("log", "/dev/null")))


def start_containers():
  containers = []
  for node_hostname, node_conf in SYS_CONF.items():
    ssh_client = SSHClient(node_hostname, node_conf["ssh"]["port"],
        node_conf["ssh"]["username"], node_conf["ssh"]["key_filename"],
        os.path.join(DIRNAME, "ssh",
        "%s-%s" % (node_hostname, "start_containers")))
    for (container_name, container_conf) in \
        node_conf.get("containers", {}).items():
      containers.append((container_conf["start_order"], node_hostname,
          node_conf, container_name, ssh_client))
  for current_start_order in sorted(set([container[0] for container in containers])):
    threads = []
    for (start_order, node_hostname, node_conf, container_name, ssh_client) in containers:
      if start_order == current_start_order:
        threads.append(threading.Thread(target=start_container,
            args=[node_hostname, node_conf, container_name, ssh_client]))
    for thread in threads:
      thread.start()
    for thread in threads:
      thread.join()


@nodes_with_monitor(".+")
def stop_monitors(node_hostname, node_conf, ssh_client):
  for monitor_name, monitor_conf in node_conf["monitors"].items():
    ssh_client.exec("sudo pkill %s" %
        monitor_conf.get("command", monitor_name).split(' ')[0])


@nodes_with_monitor(".+")
def fetch_monitoring_data(node_hostname, node_conf, ssh_client):
  for monitor_name, monitor_conf in node_conf["monitors"].items():
    if PARSE_LOG_FILES:
      if monitor_name == "collectl":
        ssh_client.exec("for filename in $(find %s -name '*.gz' -type f); do "
            "python3 /opt/BuzzBlogBenchmark/analysis/parsers/collectl_parser.py "
            "--log_filepath ${filename} --csv_filepath ${filename/.gz/.csv}; done" % monitor_conf["dirpath"])
    ssh_client.exec("tar -C {dirpath} -czf /tmp/{monitor_name}.tar.gz .".format(
        monitor_name=monitor_name, dirpath=monitor_conf["dirpath"]))
    ssh_client.copy("/tmp/{monitor_name}.tar.gz".format(
        monitor_name=monitor_name),
        os.path.join(DIRNAME, "logs", node_hostname))


@nodes_with_container(".+")
def fetch_container_logs(node_hostname, node_conf, ssh_client):
  for container_name, container_conf in node_conf["containers"].items():
    dirpath = "/tmp/%s" % container_name
    ssh_client.exec("mkdir -p {dirpath}".format(dirpath=dirpath))
    ssh_client.exec("sudo docker logs {container_name} > "
        "{dirpath}/{container_name}.log 2>&1".format(
            container_name=container_name, dirpath=dirpath))
    for filepath in container_conf.get("logs", []):
      ssh_client.exec("sudo docker cp {container_name}:{filepath} {dirpath}".\
          format(container_name=container_name, filepath=filepath,
              dirpath=dirpath))
      if PARSE_LOG_FILES:
        log_filename = os.path.basename(filepath)
        if log_filename in LOG_FILENAME_TO_PARSER:
          ssh_client.exec("python3 {parser_path} "
              "--log_filepath {log_filepath} "
              "--csv_filepath {csv_filepath}".format(
                  parser_path=LOG_FILENAME_TO_PARSER[log_filename],
                  log_filepath=os.path.join(dirpath, log_filename),
                  csv_filepath=os.path.join(dirpath, os.path.splitext(log_filename)[0] + ".csv")))
    ssh_client.exec("tar -C {dirpath} -czf {dirpath}.tar.gz .".format(
        dirpath=dirpath))
    ssh_client.copy("{dirpath}.tar.gz".format(dirpath=dirpath),
        os.path.join(DIRNAME, "logs", node_hostname))


def run():
  configure_kernel()
  get_system_specs()
  install_buzzblogbenchmark()
  install_docker()
  install_pandas()
  install_bpfcc()
  install_collectl()
  install_radvisor()
  pull_docker_images()
  copy_workload_configuration_file()
  render_configuration_templates()
  generate_backend_configuration_file()
  start_monitors()
  start_containers()
  stop_monitors()
  fetch_monitoring_data()
  fetch_container_logs()


### Main program

def main():
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(description="Run a BuzzBlog experiment")
  parser.add_argument("--description", required=True, action="store",
      type=str, help="Experiment description")
  parser.add_argument("--system_conf", required=True, action="store",
      type=str, help="Path to the system configuration file")
  parser.add_argument("--workload_conf", required=False, default="",
      action="store", type=str, help="Path to the workload configuration file")
  parser.add_argument("--docker_hub_username", required=False, default="",
      action="store", help="Docker Hub username")
  parser.add_argument("--docker_hub_password", required=False, default="",
      action="store", help="Docker Hub password")
  parser.add_argument("--parse_log_files", action="store_true")
  args = parser.parse_args()
  # Load system configuration.
  global SYS_CONF
  with open(args.system_conf) as system_conf_file:
    SYS_CONF = yaml.load(system_conf_file, Loader=yaml.Loader)
  # Load workload configuration.
  global WL_CONF
  if args.workload_conf:
    with open(args.workload_conf) as workload_conf_file:
      WL_CONF = yaml.load(workload_conf_file, Loader=yaml.Loader)
      count_loadgen_containers = count_containers("loadgen.*")
      WL_CONF["sessions"] //= count_loadgen_containers
      WL_CONF["throughput"] //= count_loadgen_containers
  # Set Docker hub credentials.
  global DOCKER_HUB_USERNAME
  DOCKER_HUB_USERNAME = args.docker_hub_username or ""
  global DOCKER_HUB_PASSWORD
  DOCKER_HUB_PASSWORD = args.docker_hub_password or ""
  # Set options.
  global PARSE_LOG_FILES
  PARSE_LOG_FILES = args.parse_log_files
  # Build backend configuration.
  global BACKEND_CONF
  for node_hostname, node_conf in SYS_CONF.items():
    for container_name, container_conf in \
        node_conf.get("containers", {}).items():
      if container_name.endswith("_service") or \
          container_name.endswith("_database") or \
          container_name.endswith("_redis"):
        container_basename = container_name[:container_name.find('_')]
        container_type = container_name[container_name.find('_') + 1:]
        container_addr = node_hostname + ":" + \
            container_conf["options"]["publish"].split(':')[0]
        if container_basename not in BACKEND_CONF:
          BACKEND_CONF[container_basename] = {"service": []}
        if container_type == "service":
          BACKEND_CONF[container_basename][container_type].append(
              container_addr)
        elif container_type == "database":
          BACKEND_CONF[container_basename][container_type] = container_addr
        elif container_type == "redis":
          BACKEND_CONF[container_basename][container_type] = container_addr
  # Create directory tree.
  global DIRNAME
  DIRNAME = "/var/log/BuzzBlogBenchmark/BuzzBlogBenchmark_%s" % timestamp()
  os.mkdir(DIRNAME)
  os.mkdir(os.path.join(DIRNAME, "conf"))
  os.mkdir(os.path.join(DIRNAME, "specs"))
  os.mkdir(os.path.join(DIRNAME, "ssh"))
  os.mkdir(os.path.join(DIRNAME, "logs"))
  for node_hostname in SYS_CONF.keys():
    os.mkdir(os.path.join(DIRNAME, "specs", node_hostname))
    os.mkdir(os.path.join(DIRNAME, "logs", node_hostname))
  # Initialize experiment metadata.
  update_metadata({"user": subprocess.getoutput("whoami"),
      "start_time": timestamp(), "description": args.description})
  # Save configuration files.
  with open(os.path.join(DIRNAME, "conf", "system.yml"), 'w') as \
      system_conf_file_copy:
    with open(args.system_conf) as system_conf_file:
      system_conf_file_copy.write(system_conf_file.read())
  if args.workload_conf:
    with open(os.path.join(DIRNAME, "conf", "workload.yml"), 'w') as \
        workload_conf_file_copy:
      with open(args.workload_conf) as workload_conf_file:
        workload_conf_file_copy.write(workload_conf_file.read())
  # Run experiment workflow.
  run()
  # Update experiment metadata.
  update_metadata({"end_time": timestamp()})


if __name__ == "__main__":
  main()
