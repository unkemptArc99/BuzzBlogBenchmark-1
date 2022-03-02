import gzip
import os
import pandas as pd
import re
import sys
import tarfile

sys.path.append(os.path.abspath(os.path.join("..")))
from parsers.loadgen_parser import LoadgenParser


def get_node_names(experiment_dirname):
    return [dirname
            for dirname in os.listdir(os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs"))
            if not dirname.startswith('.')]


def get_rpc_csvfiles(experiment_dirname):
    tarball_patterns = [
        r"^apigateway.*\.tar\.gz$",
        r"^.+_service.*\.tar\.gz$",
    ]
    for node_name in get_node_names(experiment_dirname):
        for tarball_name in os.listdir(os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname,
                "logs",  node_name)):
            if sum([1 if re.match(tarball_pattern, tarball_name) else 0 for tarball_pattern in tarball_patterns]):
                tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs",
                        node_name, tarball_name)
                with tarfile.open(tarball_path, "r:gz") as tar:
                    for filename in tar.getnames():
                        if filename.endswith("calls.csv"):
                            with tar.extractfile(filename) as csvfile:
                                yield csvfile


def get_rpc_logfiles(experiment_dirname):
    tarball_patterns = [
        r"^apigateway.*\.tar\.gz$",
        r"^.+_service.*\.tar\.gz$",
    ]
    for node_name in get_node_names(experiment_dirname):
        for tarball_name in os.listdir(os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname,
                "logs",  node_name)):
            if sum([1 if re.match(tarball_pattern, tarball_name) else 0 for tarball_pattern in tarball_patterns]):
                tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs",
                        node_name, tarball_name)
                with tarfile.open(tarball_path, "r:gz") as tar:
                    for filename in tar.getnames():
                        if filename.endswith("calls.log"):
                            with tar.extractfile(filename) as logfile:
                                yield logfile


def get_query_csvfiles(experiment_dirname):
    tarball_patterns = [
        r"^.+_service.*\.tar\.gz$",
    ]
    for node_name in get_node_names(experiment_dirname):
        for tarball_name in os.listdir(os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname,
                "logs", node_name)):
            if sum([1 if re.match(tarball_pattern, tarball_name) else 0 for tarball_pattern in tarball_patterns]):
                tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs",
                        node_name, tarball_name)
                with tarfile.open(tarball_path, "r:gz") as tar:
                    for filename in tar.getnames():
                        if filename.endswith("queries.csv"):
                            with tar.extractfile(filename) as csvfile:
                                yield csvfile


def get_query_logfiles(experiment_dirname):
    tarball_patterns = [
        r"^.+_service.*\.tar\.gz$",
    ]
    for node_name in get_node_names(experiment_dirname):
        for tarball_name in os.listdir(os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname,
                "logs", node_name)):
            if sum([1 if re.match(tarball_pattern, tarball_name) else 0 for tarball_pattern in tarball_patterns]):
                tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs",
                        node_name, tarball_name)
                with tarfile.open(tarball_path, "r:gz") as tar:
                    for filename in tar.getnames():
                        if filename.endswith("queries.log"):
                            with tar.extractfile(filename) as logfile:
                                yield logfile


def get_redis_csvfiles(experiment_dirname):
    tarball_patterns = [
        r"^.+_service.*\.tar\.gz$",
    ]
    for node_name in get_node_names(experiment_dirname):
        for tarball_name in os.listdir(os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname,
                "logs", node_name)):
            if sum([1 if re.match(tarball_pattern, tarball_name) else 0 for tarball_pattern in tarball_patterns]):
                tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs",
                        node_name, tarball_name)
                with tarfile.open(tarball_path, "r:gz") as tar:
                    for filename in tar.getnames():
                        if filename.endswith("redis.csv"):
                            with tar.extractfile(filename) as csvfile:
                                yield csvfile


def get_redis_logfiles(experiment_dirname):
    tarball_patterns = [
        r"^.+_service.*\.tar\.gz$",
    ]
    for node_name in get_node_names(experiment_dirname):
        for tarball_name in os.listdir(os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname,
                "logs", node_name)):
            if sum([1 if re.match(tarball_pattern, tarball_name) else 0 for tarball_pattern in tarball_patterns]):
                tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs",
                        node_name, tarball_name)
                with tarfile.open(tarball_path, "r:gz") as tar:
                    for filename in tar.getnames():
                        if filename.endswith("redis.log"):
                            with tar.extractfile(filename) as logfile:
                                yield logfile


def get_loadgen_csvfiles(experiment_dirname):
    for node_name in get_node_names(experiment_dirname):
        for tarball_name in os.listdir(os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname,
                "logs",  node_name)):
            if re.match(r"^loadgen.*\.tar\.gz$", tarball_name):
                tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs",
                        node_name, tarball_name)
                with tarfile.open(tarball_path, "r:gz") as tar:
                    for filename in tar.getnames():
                        if filename.endswith("loadgen.csv"):
                            with tar.extractfile(filename) as csvfile:
                                yield csvfile


def get_loadgen_logfiles(experiment_dirname):
    for node_name in get_node_names(experiment_dirname):
        for tarball_name in os.listdir(os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname,
                "logs",  node_name)):
            if re.match(r"^loadgen.*\.tar\.gz$", tarball_name):
                tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs",
                        node_name, tarball_name)
                with tarfile.open(tarball_path, "r:gz") as tar:
                    for filename in tar.getnames():
                        if filename.endswith("loadgen.log"):
                            with tar.extractfile(filename) as logfile:
                                yield logfile


def get_collectl_cpu_csvfiles(experiment_dirname):
    for node_name in get_node_names(experiment_dirname):
        tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs", node_name,
                "collectl.tar.gz")
        with tarfile.open(tarball_path, "r:gz") as tar:
            for filename in tar.getnames():
                if filename.endswith(".cpu.csv"):
                    with tar.extractfile(filename) as csvfile:
                        yield (node_name, csvfile)


def get_collectl_cpu_logfiles(experiment_dirname):
    for node_name in get_node_names(experiment_dirname):
        tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs", node_name,
                "collectl.tar.gz")
        with tarfile.open(tarball_path, "r:gz") as tar:
            for filename in tar.getnames():
                if filename.endswith(".cpu.gz"):
                    with gzip.open(tar.extractfile(filename), "rt") as logfile:
                        yield (node_name, logfile)


def get_collectl_mem_csvfiles(experiment_dirname):
    for node_name in get_node_names(experiment_dirname):
        tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs", node_name,
                "collectl.tar.gz")
        with tarfile.open(tarball_path, "r:gz") as tar:
            for filename in tar.getnames():
                if filename.endswith(".numa.csv"):
                    with tar.extractfile(filename) as csvfile:
                        yield (node_name, csvfile)


def get_collectl_mem_logfiles(experiment_dirname):
    for node_name in get_node_names(experiment_dirname):
        tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs", node_name,
                "collectl.tar.gz")
        with tarfile.open(tarball_path, "r:gz") as tar:
            for filename in tar.getnames():
                if filename.endswith(".numa.gz"):
                    with gzip.open(tar.extractfile(filename), "rt") as logfile:
                        yield (node_name, logfile)


def get_collectl_dsk_csvfiles(experiment_dirname):
    for node_name in get_node_names(experiment_dirname):
        tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs", node_name,
                "collectl.tar.gz")
        with tarfile.open(tarball_path, "r:gz") as tar:
            for filename in tar.getnames():
                if filename.endswith(".dsk.csv"):
                    with tar.extractfile(filename) as csvfile:
                        yield (node_name, csvfile)


def get_collectl_dsk_logfiles(experiment_dirname):
    for node_name in get_node_names(experiment_dirname):
        tarball_path = os.path.join(os.path.dirname(__file__), "..", "data", experiment_dirname, "logs", node_name,
                "collectl.tar.gz")
        with tarfile.open(tarball_path, "r:gz") as tar:
            for filename in tar.getnames():
                if filename.endswith(".dsk.gz"):
                    with gzip.open(tar.extractfile(filename), "rt") as logfile:
                        yield (node_name, logfile)


def get_experiment_start_time(experiment_dirname):
    requests = pd.concat([
            pd.DataFrame.from_dict(LoadgenParser(logfile).parse())
            for logfile in get_loadgen_logfiles(experiment_dirname)
    ], ignore_index=True)
    return requests["timestamp"].values.min()


def get_experiment_end_time(experiment_dirname):
    requests = pd.concat([
            pd.DataFrame.from_dict(LoadgenParser(logfile).parse())
            for logfile in get_loadgen_logfiles(experiment_dirname)
    ], ignore_index=True)
    return requests["timestamp"].values.max()
