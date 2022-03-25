# Copyright (C) 2020 Georgia Tech Center for Experimental Research in Computer
# Systems

import gzip
import os
import pandas as pd
import sys
import tarfile

sys.path.append(os.path.abspath(os.path.join("..")))
from parsers import collectl_parser, loadgen_parser, query_parser, redis_parser, rpc_parser, tcplistenbl_parser


def get_node_names(experiment_dirpath):
    return [dirname
            for dirname in os.listdir(os.path.join(experiment_dirpath, "logs"))
            if not dirname.startswith('.')]


def get_rpc_df(experiment_dirpath):
    for node_name in get_node_names(experiment_dirpath):
        for tarball_name in os.listdir(os.path.join(experiment_dirpath, "logs", node_name)):
            tarball_path = os.path.join(experiment_dirpath, "logs", node_name, tarball_name)
            with tarfile.open(tarball_path, "r:gz") as tar:
                for filename in tar.getnames():
                    if filename.endswith("calls.csv"):
                        with tar.extractfile(filename) as csvfile:
                            yield (node_name, tarball_name,
                                    pd.read_csv(csvfile, parse_dates=["timestamp"]).assign(node_name=node_name))
                            break
                else:
                    for filename in tar.getnames():
                        if filename.endswith("calls.log"):
                            with tar.extractfile(filename) as logfile:
                                yield (node_name, tarball_name,
                                        rpc_parser.RPCParser.df(logfile).assign(node_name=node_name))


def get_query_df(experiment_dirpath):
    for node_name in get_node_names(experiment_dirpath):
        for tarball_name in os.listdir(os.path.join(experiment_dirpath, "logs", node_name)):
            tarball_path = os.path.join(experiment_dirpath, "logs", node_name, tarball_name)
            with tarfile.open(tarball_path, "r:gz") as tar:
                for filename in tar.getnames():
                    if filename.endswith("queries.csv"):
                        with tar.extractfile(filename) as csvfile:
                            yield (node_name, tarball_name,
                                    pd.read_csv(csvfile, parse_dates=["timestamp"]).assign(node_name=node_name))
                            break
                else:
                    for filename in tar.getnames():
                        if filename.endswith("queries.log"):
                            with tar.extractfile(filename) as logfile:
                                yield (node_name, tarball_name,
                                        query_parser.QueryParser.df(logfile).assign(node_name=node_name))


def get_redis_df(experiment_dirpath):
    for node_name in get_node_names(experiment_dirpath):
        for tarball_name in os.listdir(os.path.join(experiment_dirpath, "logs", node_name)):
            tarball_path = os.path.join(experiment_dirpath, "logs", node_name, tarball_name)
            with tarfile.open(tarball_path, "r:gz") as tar:
                for filename in tar.getnames():
                    if filename.endswith("redis.csv"):
                        with tar.extractfile(filename) as csvfile:
                            yield (node_name, tarball_name,
                                    pd.read_csv(csvfile, parse_dates=["timestamp"]).assign(node_name=node_name))
                            break
                else:
                    for filename in tar.getnames():
                        if filename.endswith("redis.log"):
                            with tar.extractfile(filename) as logfile:
                                yield (node_name, tarball_name,
                                        redis_parser.RedisParser.df(logfile).assign(node_name=node_name))


def get_loadgen_df(experiment_dirpath):
    for node_name in get_node_names(experiment_dirpath):
        for tarball_name in os.listdir(os.path.join(experiment_dirpath, "logs", node_name)):
            tarball_path = os.path.join(experiment_dirpath, "logs", node_name, tarball_name)
            with tarfile.open(tarball_path, "r:gz") as tar:
                for filename in tar.getnames():
                    if filename.endswith("loadgen.csv"):
                        with tar.extractfile(filename) as csvfile:
                            yield (node_name, tarball_name,
                                    pd.read_csv(csvfile, parse_dates=["timestamp"]).assign(node_name=node_name))
                            break
                else:
                    for filename in tar.getnames():
                        if filename.endswith("loadgen.log"):
                            with tar.extractfile(filename) as logfile:
                                yield (node_name, tarball_name,
                                        loadgen_parser.LoadgenParser.df(logfile).assign(node_name=node_name))


def get_collectl_cpu_df(experiment_dirpath):
    for node_name in get_node_names(experiment_dirpath):
        for tarball_name in os.listdir(os.path.join(experiment_dirpath, "logs", node_name)):
            tarball_path = os.path.join(experiment_dirpath, "logs", node_name, tarball_name)
            with tarfile.open(tarball_path, "r:gz") as tar:
                for filename in tar.getnames():
                    if filename.endswith(".cpu.csv"):
                        with tar.extractfile(filename) as csvfile:
                            yield (node_name, tarball_name,
                                    pd.read_csv(csvfile, parse_dates=["timestamp"]).assign(node_name=node_name))
                            break
                else:
                    for filename in tar.getnames():
                        if filename.endswith(".cpu.gz"):
                            with gzip.open(tar.extractfile(filename), "rt") as logfile:
                                yield (node_name, tarball_name,
                                        collectl_parser.CollectlParser.df(logfile, "cpu").assign(node_name=node_name))


def get_collectl_mem_df(experiment_dirpath):
    for node_name in get_node_names(experiment_dirpath):
        for tarball_name in os.listdir(os.path.join(experiment_dirpath, "logs", node_name)):
            tarball_path = os.path.join(experiment_dirpath, "logs", node_name, tarball_name)
            with tarfile.open(tarball_path, "r:gz") as tar:
                for filename in tar.getnames():
                    if filename.endswith(".numa.csv"):
                        with tar.extractfile(filename) as csvfile:
                            yield (node_name, tarball_name,
                                    pd.read_csv(csvfile, parse_dates=["timestamp"]).assign(node_name=node_name))
                            break
                else:
                    for filename in tar.getnames():
                        if filename.endswith(".numa.gz"):
                            with gzip.open(tar.extractfile(filename), "rt") as logfile:
                                yield (node_name, tarball_name,
                                        collectl_parser.CollectlParser.df(logfile, "mem").assign(node_name=node_name))


def get_collectl_dsk_df(experiment_dirpath):
    for node_name in get_node_names(experiment_dirpath):
        for tarball_name in os.listdir(os.path.join(experiment_dirpath, "logs", node_name)):
            tarball_path = os.path.join(experiment_dirpath, "logs", node_name, tarball_name)
            with tarfile.open(tarball_path, "r:gz") as tar:
                for filename in tar.getnames():
                    if filename.endswith(".dsk.csv"):
                        with tar.extractfile(filename) as csvfile:
                            yield (node_name, tarball_name,
                                    pd.read_csv(csvfile, parse_dates=["timestamp"]).assign(node_name=node_name))
                            break
                else:
                    for filename in tar.getnames():
                        if filename.endswith(".dsk.gz"):
                            with gzip.open(tar.extractfile(filename), "rt") as logfile:
                                yield (node_name, tarball_name,
                                        collectl_parser.CollectlParser.df(logfile, "dsk").assign(node_name=node_name))


def get_tcplistenbl_df(experiment_dirpath):
    tarball_name = "tcplistenbl-bpftrace.tar.gz"
    for node_name in get_node_names(experiment_dirpath):
        if tarball_name in os.listdir(os.path.join(experiment_dirpath, "logs", node_name)):
            tarball_path = os.path.join(experiment_dirpath, "logs", node_name, tarball_name)
            with tarfile.open(tarball_path, "r:gz") as tar:
                if "./log.csv" in tar.getnames():
                    with tar.extractfile("./log.csv") as csvfile:
                        yield (node_name, tarball_name,
                                pd.read_csv(csvfile, parse_dates=["timestamp"]).assign(node_name=node_name))
                elif "./log" in tar.getnames():
                    with tar.extractfile("./log") as logfile:
                        yield (node_name, tarball_name, tcplistenbl_parser.TcplistenblParser.df(logfile).assign(node_name=node_name))


def get_experiment_start_time(experiment_dirpath):
    requests = pd.concat([df[2] for df in get_loadgen_df(experiment_dirpath)])
    return requests["timestamp"].values.min()


def get_experiment_end_time(experiment_dirpath):
    requests = pd.concat([df[2] for df in get_loadgen_df(experiment_dirpath)])
    return requests["timestamp"].values.max()
