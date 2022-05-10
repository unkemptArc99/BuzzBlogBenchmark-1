import argparse
import os
import sys
import warnings

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(os.path.abspath(os.path.join("..")))
from utils.utils import *

class Experiment:

    EXPERIMENT_DIRNAME = None
    RAMP_UP_DURATION = None
    RAMP_DOWN_DURATION = None

    OUTPUT_DIRECTORY = None

    experiment_dirpath = None
    output_dirpath = None
    loadgen_requests = None
    rpc_requests = None
    function_names = None
    functions_of_interest = ['account:retrieve_standard_account',
                             'like:count_likes_of_post',
                             'like:list_likes',
                             'post:retrieve_expanded_post',
                             'uniquepair:count',
                             'uniquepair:fetch']
    bl = None
    node_names = None
    nodes_of_interest = {'node-8': 'Account Service',
                        'node-9': 'Account DB',
                        'node-11': 'Like Service',
                        'node-12': 'Post Service',
                        'node-13': 'Post DB',
                        'node-14': 'Uniquepair Service',
                        'node-15': 'Uniquepair DB'}
    start_time = None
    max_latency_in_s = None
    n_request_types = None

    successful_requests_num = None
    failed_requests_num = None

    read_requests = None
    write_requests = None

    df = None

    def __init__(self, ex_dir, ru, rd, out_dir):
        self.EXPERIMENT_DIRNAME = ex_dir
        self.RAMP_UP_DURATION = int(ru)
        self.RAMP_DOWN_DURATION = int(rd)
        self.OUTPUT_DIRECTORY = out_dir
        self.experiment_dirpath = os.path.join(os.path.abspath(""), "..", "data", \
                                                self.EXPERIMENT_DIRNAME)
        self.output_dirpath = os.path.join(os.path.abspath(""), "..", "data", \
                                                self.OUTPUT_DIRECTORY)

    def cache_request(self):
        print("Loadgen Request Caching Start...")
        self.loadgen_requests = pd.concat([df[2] for df in get_loadgen_df(self.experiment_dirpath)])
        self.start_time = get_experiment_start_time(self.experiment_dirpath)
        self.max_latency_in_s = int(self.loadgen_requests["latency"].max()) + 1.0
        self.n_request_types = len(self.loadgen_requests.type.unique())
        self.loadgen_requests["timestamp"] = self.loadgen_requests.apply(
            lambda r: (r["timestamp"] - self.start_time).total_seconds(), axis=1)
        self.loadgen_requests["window_1000"] = self.loadgen_requests["timestamp"].\
            round(0).multiply(1000)
        self.loadgen_requests["window_10"] = self.loadgen_requests["timestamp"].\
            round(2).multiply(1000)
        self.loadgen_requests.set_index("timestamp", inplace=True)
        self.loadgen_requests.sort_index(inplace=True)
        print("Loadgen Request Cache Complete.")

        print("RPC Request Caching Start...")
        self.rpc_requests = pd.concat([df[2] for df in get_rpc_df(self.experiment_dirpath)])
        self.function_names = sorted(self.rpc_requests["function"].unique())
        self.rpc_requests["timestamp"] = self.rpc_requests.apply(lambda r: (r["timestamp"] - self.start_time).total_seconds(), axis=1)
        self.rpc_requests["latency"] = self.rpc_requests["latency"].multiply(1000)
        self.rpc_requests["window_1000"] = self.rpc_requests["timestamp"].round(0).multiply(1000)
        self.rpc_requests["window_10"] = self.rpc_requests["timestamp"].round(2).multiply(1000)
        self.rpc_requests.set_index("timestamp", inplace=True)
        self.rpc_requests.sort_index(inplace=True)
        print("RPC Request Cache Complete.")

        print("TCP Backlog Cache Start...")
        self.bl =  pd.concat([df[2] for df in get_tcplistenbl_df(self.experiment_dirpath)])
        self.node_names = get_node_names(self.experiment_dirpath)
        self.bl["timestamp"] = self.bl.apply(lambda r: (r["timestamp"] - self.start_time).total_seconds(), axis=1)
        self.bl["window_1000"] = self.bl["timestamp"].round(0).multiply(1000)
        self.bl["window_10"] = self.bl["timestamp"].round(2).multiply(1000)
        self.bl.set_index("timestamp", inplace=True)
        self.bl.sort_index(inplace=True)
        print("TCP Backlog Cache Complete.")

    def success_fail_metric(self):
        self.df = self.loadgen_requests[(self.loadgen_requests.index >= self.RAMP_UP_DURATION)]
        self.df = self.loadgen_requests[(self.loadgen_requests.index <= \
            self.loadgen_requests.index.max() - self.RAMP_DOWN_DURATION)]
        df_temp = self.df.groupby(["status"]).count()["method"]
        self.successful_requests_num = df_temp['successful']
        self.failed_requests_num = df_temp['failed']
        with open(os.path.join(self.output_dirpath, 'stats.txt'), 'a') as f:
            f.write('Requests Success/Fail Metrics\n')
            f.write('-----------------------------\n')
            f.write('Successful Requests: ' + str(self.successful_requests_num) + '\n')
            f.write('Failed Requests: ' + str(self.failed_requests_num) + '\n')
            f.write('\n')

    def rw_metric(self):
        df_temp = self.df.groupby(["rw"]).count()["method"]
        self.read_requests = df_temp['read']
        self.write_requests = df_temp['write']
        with open(os.path.join(self.output_dirpath, 'stats.txt'), 'a') as f:
            f.write('Read/Write Metrics\n')
            f.write('------------------\n')
            f.write('Read Requests: ' + str(self.read_requests) + '\n')
            f.write('Write Requests: ' + str(self.write_requests) + '\n')
            f.write('\n')

    def lat_distr(self):
        LATENCY_BIN_IN_MS = 200
        # Data frame
        df = self.df[(self.df["status"] == "successful")]
        df["latency_bin"] = df.apply(
            lambda r: int(r["latency"] * 1000 // LATENCY_BIN_IN_MS), axis=1)
        p999 = df["latency"].quantile(0.999) * 1000
        p50 = df["latency"].quantile(0.50) * 1000
        # Plot
        fig = plt.figure(figsize=(24, 12))
        ax = fig.gca(xlabel="Latency (millisec)", ylabel="Requests (count)")
        ax.grid(alpha=0.75)
        ax.set_yscale("log")
        ax.set_xlim((0, (1000 // LATENCY_BIN_IN_MS) * self.max_latency_in_s))
        ax.set_xticks(range(int((1000 // LATENCY_BIN_IN_MS) * self.max_latency_in_s) + 1))
        ax.set_xticklabels(
            range(0, \
                (int((1000 // LATENCY_BIN_IN_MS) * self.max_latency_in_s) \
                    + 1) * LATENCY_BIN_IN_MS, LATENCY_BIN_IN_MS))
        ax.axvline(x=p50 / LATENCY_BIN_IN_MS, ls="dotted", lw=5, color="darkorange")
        ax.text(x=p50 / LATENCY_BIN_IN_MS, y=1000, s=" P50", fontsize=22, color="darkorange")
        ax.axvline(x=p999 / LATENCY_BIN_IN_MS, ls="dotted", lw=5, color="darkorange")
        ax.text(x=p999 / LATENCY_BIN_IN_MS, y=100, s=" P99.9", fontsize=22, color="darkorange")
        df["latency_bin"].plot(ax=ax, kind="hist", \
            title="Latency Distribution of Successful Requests Excluding Ramping Periods", \
                bins=range(int((1000 // LATENCY_BIN_IN_MS) * self.max_latency_in_s)), grid=True)
        fig.savefig(os.path.join(self.output_dirpath, 'latdist.png'))

    def pit_graph(self):
        # Data frame
        df = self.loadgen_requests[self.loadgen_requests["status"] == "successful"]
        df = df.groupby(["window_1000"])["latency"].max().reindex(
            range(0, int(df["window_1000"].max()) + 1, 1000), fill_value=0)
        # Plot
        fig = plt.figure(figsize=(24, 12))
        ax = fig.gca()
        ax.grid(alpha=0.75)
        ax.set_xlim((int(df.index.min()), int(df.index.max())))
        ax.set_ylim((0, self.max_latency_in_s))
        ax.axvline(x=self.RAMP_UP_DURATION * 1000, ls="--", color="green")
        ax.axvline(x=df.index.max() - (self.RAMP_DOWN_DURATION * 1000), ls="--", color="green")
        df.plot(
            ax=ax,
            kind="line",
            title="Latency of Successful Requests",
            xlabel="Time (millisec)",
            ylabel="Latency (sec)",
            color="purple",
            grid=True,
            xticks=range(int(df.index.min()), int(df.index.max()) + 1, 60000)
            )
        fig.savefig(os.path.join(self.output_dirpath, 'pit_graph.png'))

    def thput_graph(self):
        # Data frame
        df = self.loadgen_requests.groupby(["window_1000", "status"])["window_1000"].count().unstack().fillna(0)
        df = df.reindex(range(0, int(df.index.max()) + 1, 1000), fill_value=0)
        # Plot
        fig = plt.figure(figsize=(24, 12))
        ax = fig.gca()
        ax.grid(alpha=0.75)
        ax.axvline(x=self.RAMP_UP_DURATION * 1000, ls="--", color="green")
        ax.axvline(x=self.loadgen_requests.index.values.max() - (self.RAMP_DOWN_DURATION * 1000), ls="--", color="green")
        ax.set_xlim((int(df.index.min()), int(df.index.max())))
        df.plot(
            ax=ax,
            kind="line",
            title="Throughput (requests per second)",
            xlabel="Time (millisec)",
            ylabel="Requests (count)",
            color={"failed": "red", "successful": "blue"},
            legend=True,
            grid=True,
            xticks=range(int(df.index.min()), int(df.index.max()) + 1, 60000)
            )
        fig.savefig(os.path.join(self.output_dirpath, 'thput_graph.png'))

    def print_summary(self):
        df = self.loadgen_requests[(self.loadgen_requests.index >= self.RAMP_UP_DURATION) & (self.loadgen_requests.index <= self.loadgen_requests.index.max() - self.RAMP_DOWN_DURATION)]
        with open(os.path.join(self.output_dirpath, 'stats.txt'), 'a') as f:
            f.write("Summary\n")
            f.write("-------\n")
            f.write("Number of requests (Excluding Ramping Up and Down Periods)\n")
            f.write("  Total:       %7d\n" % df.shape[0])
            f.write("  Status\n")
            f.write("    Failed:    %7d (%9.5f%%)\n" % (df[df["status"] == "failed"]["status"].count(),
                (df[df["status"] == "failed"]["status"].count() / df.shape[0]) * 100))
            f.write("    Succesful: %7d (%9.5f%%)\n" % (df[df["status"] == "successful"]["status"].count(),
                (df[df["status"] == "successful"]["status"].count() / df.shape[0]) * 100))
            f.write("  Type")
            f.write("    Read:      %7d (%9.5f%%)\n" % (df[df["rw"] == "read"]["rw"].count(),
                (df[df["rw"] == "read"]["rw"].count() / df.shape[0]) * 100))
            f.write("    Write:     %7d (%9.5f%%)\n" % (df[df["rw"] == "write"]["rw"].count(),
                (df[df["rw"] == "write"]["rw"].count() / df.shape[0]) * 100))
            f.write("Experiment duration (s)\n")
            f.write("  Total:       %7.3f" % (df.index.values.max() - df.index.values.min()))
            f.write("Latency (ms)\n")
            f.write("P99.9:         %7.2f\n" % (df[df["status"] == "successful"]["latency"].quantile(0.999) * 1000))
            f.write("  P99:         %7.2f\n" % (df[df["status"] == "successful"]["latency"].quantile(0.99) * 1000))
            f.write("  P95:         %7.2f\n" % (df[df["status"] == "successful"]["latency"].quantile(0.95) * 1000))
            f.write("  P50:         %7.2f\n" % (df[df["status"] == "successful"]["latency"].quantile(0.50) * 1000))
            f.write("  Avg:         %7.2f\n" % (df[df["status"] == "successful"]["latency"].mean() * 1000))
            f.write("  Std:         %7.2f\n" % (df[df["status"] == "successful"]["latency"].std() * 1000))
            f.write("Throughput (req/s)\n")
            f.write("  P99:         %7.2f\n" % df.groupby(["window_1000"])["window_1000"].count().reindex(range(int(df["window_1000"].min()), int(df["window_1000"].max()) + 1, 1000), fill_value=0).quantile(0.99))
            f.write("  P95:         %7.2f\n" % df.groupby(["window_1000"])["window_1000"].count().reindex(range(int(df["window_1000"].min()), int(df["window_1000"].max()) + 1, 1000), fill_value=0).quantile(0.95))
            f.write("  P50:         %7.2f\n" % df.groupby(["window_1000"])["window_1000"].count().reindex(range(int(df["window_1000"].min()), int(df["window_1000"].max()) + 1, 1000), fill_value=0).quantile(0.50))
            f.write("  Avg:         %7.2f\n" % df.groupby(["window_1000"])["window_1000"].count().reindex(range(int(df["window_1000"].min()), int(df["window_1000"].max()) + 1, 1000), fill_value=0).mean())
            f.write("  Std:         %7.2f\n" % df.groupby(["window_1000"])["window_1000"].count().reindex(range(int(df["window_1000"].min()), int(df["window_1000"].max()) + 1, 1000), fill_value=0).std())
            f.write("\n")

    def rpc(self):
        self.rpc_lat_distr()
        self.rpc_pit_graph()
        self.rpc_stats()

    def rpc_lat_distr(self):
        LATENCY_BIN_IN_MS = 200
        fig = plt.figure(figsize=(24, len(self.functions_of_interest) * 12))
        for (i, function) in enumerate(self.functions_of_interest):
            # Data frame
            df = self.rpc_requests[(self.rpc_requests["function"] == function)]
            if df.empty:
                continue
            df["latency_bin"] = df.apply(lambda r: int(r["latency"] // LATENCY_BIN_IN_MS), axis=1)
            p999 = df["latency"].quantile(0.999)
            p50 = df["latency"].quantile(0.50)
            # Plot
            ax = fig.add_subplot(len(self.functions_of_interest), 1, i + 1)
            ax.set_yscale("log")
            ax.grid(alpha=0.75)
            ax.set_xlim((0, (1000 // LATENCY_BIN_IN_MS) * self.max_latency_in_s))
            ax.set_xticks(range(int((1000 // LATENCY_BIN_IN_MS) * self.max_latency_in_s) + 1))
            ax.set_xticklabels(
                range(
                    0, 
                    (int((1000 // LATENCY_BIN_IN_MS) * self.max_latency_in_s) + 1) * LATENCY_BIN_IN_MS, 
                    LATENCY_BIN_IN_MS
                    )
                )
            ax.axvline(x=p50 / LATENCY_BIN_IN_MS, ls="dotted", lw=5, color="darkorange")
            ax.text(x=p50 / LATENCY_BIN_IN_MS, y=10, s=" P50", fontsize=22, color="darkorange")
            ax.axvline(x=p999 / LATENCY_BIN_IN_MS, ls="dotted", lw=5, color="darkorange")
            ax.text(x=p999 / LATENCY_BIN_IN_MS, y=10, s=" P99.9", fontsize=22, color="darkorange")
            df["latency_bin"].plot(
                ax=ax, 
                kind="hist", 
                title="Latency Distribution - %s" % function, 
                xlabel="Latency (milliseconds)", 
                ylabel="Calls (count)", 
                bins=range((1000 // LATENCY_BIN_IN_MS) * int(self.max_latency_in_s)), 
                grid=True
                )
            plt.subplots_adjust(hspace=0.25)
        fig.savefig(os.path.join(self.output_dirpath, 'rpc_lat_dist.png'))

    def rpc_pit_graph(self):
        fig = plt.figure(figsize=(24, len(self.functions_of_interest) * 12))
        for (i, function) in enumerate(self.functions_of_interest):
            # Data frame
            df = self.rpc_requests[(self.rpc_requests["function"] == function)].groupby(["window_1000"])["latency"].max().reindex(
                range(0, int(self.rpc_requests["window_1000"].max()) + 1, 1000), fill_value=0)
            # Plot
            ax = fig.add_subplot(len(self.functions_of_interest), 1, i + 1)
            ax.grid(alpha=0.75)
            ax.set_xlim((0, int(df.index.max())))
            ax.set_ylim((0, df.values.max()))
            df.plot(
                ax=ax, 
                kind="line", 
                title="Instantaneous Latency - %s" % function, 
                xlabel="Time (millisec)", 
                ylabel="Latency (millisec)", 
                grid=True
                )
            plt.subplots_adjust(hspace=0.25)
        fig.savefig(os.path.join(self.output_dirpath, 'rpc_pit_graph.png'))

    # def list_service_server_queue(self):

    # def list_service_cpu(self):

    def rpc_stats(self):
        for (i, function) in enumerate(self.functions_of_interest):
            df = self.rpc_requests[(self.rpc_requests["function"] == function)]
            with open(os.path.join(self.output_dirpath, 'stats.txt'), 'a') as f:
                f.write('RPC Summary\n')
                f.write('-----------\n')
                f.write(function)
                f.write("  Number of RPCs/s")
                f.write("    Total:       %7d" % df.shape[0])
                f.write("    Avg:         %7.2f" % (df.shape[0] / (df.index.max() - df.index.min())))
                f.write("  Latency (ms)")
                f.write(" P99.99:         %7.2f" % (df["latency"].quantile(0.9999)))
                f.write("  P99.9:         %7.2f" % (df["latency"].quantile(0.999)))
                f.write("    P99:         %7.2f" % (df["latency"].quantile(0.99)))
                f.write("    P95:         %7.2f" % (df["latency"].quantile(0.95)))
                f.write("    P50:         %7.2f" % (df["latency"].quantile(0.50)))
                f.write("    Avg:         %7.2f" % (df["latency"].mean()))
                f.write("    Std:         %7.2f" % (df["latency"].std()))
                f.write("\n")

    def print(self):
        print(self.EXPERIMENT_DIRNAME)
        print(self.RAMP_UP_DURATION)
        print(self.RAMP_DOWN_DURATION)
        print(self.OUTPUT_DIRECTORY)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot List Likes graph experiment")
    parser.add_argument('experiment_dirname', type=str,
                        help="The experiment's directory name (stored in analysis/data)")
    parser.add_argument('ramp_up', type=int,
                        help="Ramp Up Duration of the experiment")
    parser.add_argument('ramp_down', type=int,
                        help="Ramp Down Duration of the experiment")
    parser.add_argument('output_directory', type=str,
                        help='Path of the Output Directory, where the plots will be stored, \
                            with respective to analysis/notebooks')

    args = parser.parse_args()
    if not os.path.isdir(os.path.join(os.path.abspath(""), '..', 'data', args.experiment_dirname)):
        raise FileNotFoundError("Input Directory not found")
    if not os.path.isdir(os.path.join(os.path.abspath(""), '..', 'data', args.output_directory)):
        os.mkdir(os.path.join(os.path.abspath(""), '..', 'data', args.output_directory))
    exp = Experiment(args.experiment_dirname, args.ramp_up, args.ramp_down, args.output_directory)
    # exp.print()
    exp.cache_request()
    exp.success_fail_metric()
    exp.rw_metric()
    exp.lat_distr()
    exp.pit_graph()
    exp.thput_graph()
    exp.print_summary()
    exp.rpc()
