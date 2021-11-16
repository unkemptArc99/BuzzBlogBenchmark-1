# Copyright (C) 2020 Georgia Tech Center for Experimental Research in Computer
# Systems

"""
Simple dataclass-based parsers for both rAdvisor target (container) logs
and buffer flush logs
"""

from dataclasses import dataclass
from typing import List, Dict, Iterable, Any, Tuple, Union, OrderedDict
from yaml import Loader
import csv

# Minimum target log version that this supports
MIN_TARGET_LOG_VERSION="1.3.0"


@dataclass
class IOStats:
    read: int
    write: int
    sync: int
    asyn: int


@dataclass
class TargetLogEntry:
    read: int
    # PID stats
    pids_current: int
    pids_max: Union[int, str]
    # CPU stats
    cpu_usage_total: int
    cpu_usage_system: int
    cpu_usage_user: int
    cpu_usage_percpu: List[int]
    cpu_stat_user: int
    cpu_stat_system: int
    cpu_throttling_periods: int
    cpu_throttling_throttled_count: int
    cpu_throttling_throttled_time: int
    # Memory stats
    memory_usage_current: int
    memory_usage_max: int
    memory_limit_hard: int
    memory_limit_soft: int
    memory_failcnt: int
    memory_hierarchical_limit_memory: int
    memory_hierarchical_limit_memoryswap: int
    memory_cache: int
    memory_rss_all: int
    memory_rss_huge: int
    memory_mapped: int
    memory_swap: int
    memory_paged_in: int
    memory_paged_out: int
    memory_fault_total: int
    memory_fault_major: int
    memory_anon_inactive: int
    memory_anon_active: int
    memory_file_inactive: int
    memory_file_active: int
    memory_unevictable: int
    # Block IO stats
    blkio_time: int
    blkio_sectors: int
    blkio_service_bytes: IOStats
    blkio_service_ios: IOStats
    blkio_service_time: IOStats
    blkio_queued: IOStats
    blkio_wait: IOStats
    blkio_merged: IOStats
    blkio_throttle_service_bytes: IOStats
    blkio_throttle_service_ios: IOStats
    blkio_bfq_service_bytes: IOStats
    blkio_bfq_service_ios: IOStats

    @staticmethod
    def make(row: Dict[str, str]) -> 'TargetLogEntry':
        def i(key: str) -> int:
            """Attempts to parse a cell to an int, or returns 0"""
            if key in row and row[key] is not None and len(row[key]) > 0:
                return int(row[key])
            return 0

        def io(key_prefix: str) -> IOStats:
            """Makes an IOStats instance from the key prefix"""
            return IOStats(
                read=i(f"{key_prefix}.read"),
                write=i(f"{key_prefix}.write"),
                sync=i(f"{key_prefix}.sync"),
                asyn=i(f"{key_prefix}.async"))

        return TargetLogEntry(
            read=int(row["read"]),
            pids_current=i("pids.current"),
            pids_max="max" if row["pids.max"] == "max" else i("pids.max"),
            # CPU stats
            cpu_usage_total=i("cpu.usage.total"),
            cpu_usage_system=i("cpu.usage.system"),
            cpu_usage_user=i("cpu.usage.user"),
            cpu_usage_percpu=([] if row["cpu.usage.percpu"] == ""
                else list(map(int, row["cpu.usage.percpu"].split(" ")))),
            cpu_stat_user=i("cpu.stat.user"),
            cpu_stat_system=i("cpu.stat.system"),
            cpu_throttling_periods=i("cpu.throttling.periods"),
            cpu_throttling_throttled_count=i("cpu.throttling.throttled.count"),
            cpu_throttling_throttled_time=i("cpu.throttling.throttled.time"),
            # Memory stats
            memory_usage_current=i("memory.usage.current"),
            memory_usage_max=i("memory.usage.max"),
            memory_limit_hard=i("memory.limit.hard"),
            memory_limit_soft=i("memory.limit.soft"),
            memory_failcnt=i("memory_failcnt"),
            memory_hierarchical_limit_memory=i("memory.hierarchical.limit.memory"),
            memory_hierarchical_limit_memoryswap=i("memory.hierarchical.limit.memoryswap"),
            memory_cache=i("memory.cache"),
            memory_rss_all=i("memory.rss.all"),
            memory_rss_huge=i("memory.rss.huge"),
            memory_mapped=i("memory.mapped"),
            memory_swap=i("memory.swap"),
            memory_paged_in=i("memory.paged.in"),
            memory_paged_out=i("memory.paged.out"),
            memory_fault_total=i("memory.fault.total"),
            memory_fault_major=i("memory.fault.major"),
            memory_anon_inactive=i("memory.anon.inactive"),
            memory_anon_active=i("memory.anon.active"),
            memory_file_inactive=i("memory.file.inactive"),
            memory_file_active=i("memory.file.active"),
            memory_unevictable=i("memory.unevictable"),
            # Block IO stats
            blkio_time=i("blkio.time"),
            blkio_sectors=i("blkio.sectors"),
            blkio_service_bytes=io("blkio.service.bytes"),
            blkio_service_ios=io("blkio.service.ios"),
            blkio_service_time=io("blkio.service.time"),
            blkio_queued=io("blkio.queued"),
            blkio_wait=io("blkio.wait"),
            blkio_merged=io("blkio.merged"),
            blkio_throttle_service_bytes=io("blkio.throttle.service.bytes"),
            blkio_throttle_service_ios=io("blkio.throttle.service.ios"),
            blkio_bfq_service_bytes=io("blkio.bfq.service.bytes"),
            blkio_bfq_service_ios=io("blkio.bfq.service.ios"))


@dataclass
class BufferFlushLogEntry:
    timestamp: int
    target_id: str
    written: int
    success: bool

    @staticmethod
    def make(row: Dict[str, str]) -> 'BufferFlushLogEntry':
        return BufferFlushLogEntry(
            timestamp=int(row["timestamp"]),
            target_id=row["target_id"],
            written=int(row["written"]),
            success=row["success"].lower() == 'true')


def parse_target_log(lines: Iterable[str]) -> Tuple[Iterable[TargetLogEntry], Dict[str, Any]]:
    """
    Loads an output target file from rAdvisor into
    a lazy iterator of TargetLogEntry in the order of logging,
    in addition to the metadata dictionary contained at the top of the logfile.
    """

    metadata = {}
    yaml_lines = []

    # Skip the first yaml delimeter
    next(lines)

    # Load all lines until the end of the yaml section
    while True:
        try:
            line = next(lines)
        except StopIteration:
            break
        else:
            if line.startswith("---"):
                break
            yaml_lines.append(line)

    # Load YAML to dictionary
    yaml_str = "\n".join(yaml_lines)
    yaml_loader = Loader(yaml_str)
    metadata = yaml_loader.get_data()

    # Check the version string
    version = metadata.get("Version", "0.0.0")
    if version < MIN_TARGET_LOG_VERSION:
        print(f"Warning: rAdvisor log version '{version}' "
            f"is less than minimum version '{MIN_TARGET_LOG_VERSION}'")
    
    csv_reader = csv.DictReader(lines)
    def generator():
        for row in csv_reader:
            try:
                yield TargetLogEntry.make(row)
            except Exception as e:
                print(e)
                print("An error ocurred. continuing...\n")

    return (generator(), metadata)


def parse_buffer_flush_log(lines: Iterable[str]) -> OrderedDict[int, BufferFlushLogEntry]:
    """
    Loads a buffer flush log from rAdvisor into an ordered dictionary
    of timestamp (int) -> BufferFlushLogEntry in the order of logging.
    """

    entries = OrderedDict()
    csv_reader = csv.DictReader(lines)
    try:
        for row in csv_reader:
            log_entry = BufferFlushLogEntry.make(row)
            entries[log_entry.timestamp] = log_entry
    except Exception as e:
        print(e)
        print("An error ocurred. continuing...\n")

    return entries
