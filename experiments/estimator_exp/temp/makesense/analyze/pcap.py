import pdb
import subprocess
from os.path import join as pj
import pandas as pd
import os

BIN = 25


def ipv6_to_host(s):
    return int(s.split(":")[-1:][0], 16)


def pcap2csv(folder):
    """
    Execute a simple filter on PCAP and count
    """
    print("start pcap2csv")
    with open(pj(folder, "results", "pcap.csv"), "w") as output_file:
        command = ["tshark",
                   "-T", "fields",
                   "-E", "header=y",
                   "-E", "separator=,",
                   "-e", "frame.time_relative",
                   "-e", "frame.len",
                   "-e", "wpan.src64",
                   "-e", "wpan.dst64",
                   "-e", "icmpv6.type",
                   "-e", "ipv6.src",
                   "-e", "ipv6.dst",
                   "-e", "icmpv6.code",
                   "-e", "data.data",
                   "-r", pj(folder, "output.pcap")]
        print(str(command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output_file.write(stdout)


def format_pcap_csv(folder):
    df = pd.read_csv(pj(folder, "results", "pcap.csv"))
    df.rename(columns={"frame.time_relative": "time",
                       "frame.len": "length",
                       "wpan.src64": "mac_src",
                       "wpan.dst64": "mac_dst",
                       "ipv6.src": "ip_src",
                       "icmpv6.type": "icmpv6_type",
                       "ipv6.dst": "ip_dst",
                       "icmpv6.code": "icmp_code",
                       "data.data": "payload"
                       }, inplace=True)

    SIM_TIME = 200
    df["time"] *= SIM_TIME / df.time.max()

    def f(x):
        if isinstance(x["mac_dst"], str):
            try:
                return ipv6_to_host(x["mac_dst"])
            except:
                return x["mac_dst"]
    df.mac_dst = df.apply(f, axis=1)

    def f(x):
        if isinstance(x["mac_src"], str):
            try:
                return ipv6_to_host(x["mac_src"])
            except:
                return x["mac_src"]
    df.mac_src = df.apply(f, axis=1)

    def f(x):
        if isinstance(x["ip_src"], str):
            try:
                
                return ipv6_to_host(x["ip_src"])
            except:
                return x["ip_src"]
    df.ip_src = df.apply(f, axis=1)

    df.icmpv6_type = df.icmpv6_type.apply(lambda x: "rpl" if x == 155 else x)
    code = {0: "dis", 1: "dio", 2: "dao"}
    df.icmp_code = df.icmp_code.apply(lambda x: code[x] if x in code else x)

    def f(x):
        if isinstance(x["payload"], str):
            return "udp"
        else:
            return x["icmpv6_type"]
    df.icmpv6_type = df.apply(f, axis=1)

    # ACK packets
    def f(x):
        if x["length"] == 5:
            return "ack"
        else:
            return x["icmpv6_type"]
    df.icmpv6_type = df.apply(f, axis=1)

    # Forwarding
    def f(x):
        if x.icmpv6_type == "udp":
            if x.mac_src != x.ip_src:
                return True
            else:
                return False
        else:
            return False
    df["forwarding"] = df.apply(f, axis=1)

    df.to_csv(pj(folder, "results", "pcap_relooked.csv"), index=False)


def dashboard(folder):
    df = pd.read_csv(pj(folder, "results", "pcap_relooked.csv"))

    df["bin_start"] = BIN * (df.time // BIN)

    bin_df = pd.DataFrame()
    bin_df["total"] = df.groupby("bin_start").length.sum()
    bin_df["udp"] = df[df.icmpv6_type == "udp"].groupby("bin_start").length.sum()
    bin_df["rpl"] = df[df.icmpv6_type == "rpl"].groupby("bin_start").length.sum()
    bin_df["forwarding"] = df[df.forwarding].groupby("bin_start").length.sum()
    bin_df.to_csv(pj(folder, "results", "bin_global.csv"))

    for target in pd.Series(df.mac_src.values.ravel()).unique():
        if target > 1:
            node_df = df[df.mac_src == target]
            bin_df = pd.DataFrame()
            bin_df["total"] = node_df.groupby("bin_start").length.sum()
            bin_df["udp"] = node_df[node_df.icmpv6_type == "udp"].groupby("bin_start").length.sum()
            bin_df["rpl"] = node_df[node_df.icmpv6_type == "rpl"].groupby("bin_start").length.sum()
            bin_df["forwarding"] = node_df[node_df.forwarding].groupby("bin_start").length.sum()

            # Conversion from bytes to time
            RATE = 250000
            bin_df = 8.0 * bin_df / RATE

            output_folder = pj(folder, "results", "protocol_repartition")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            bin_df.to_csv(pj(output_folder, "protocol_repartition_%d.csv" % target))

            estimation_noinfo = pd.read_csv(pj(folder, "results", "estimation", "bin_estimation_%d_noinfo.csv" % target))
            estimation_noinfo.rename(columns={"tx_estimated": "tx_noinfo", "rx_estimated": "rx_noinfo"}, inplace=True)

            estimation_noinfo = estimation_noinfo[["bin_start",
                                                   "tx_noinfo",
                                                   "rx_noinfo"]]

            estimation_route = pd.read_csv(pj(folder, "results", "estimation", "bin_estimation_%d_route.csv" % target))
            estimation_route.rename(columns={"tx_estimated": "tx_route", "rx_estimated": "rx_route"}, inplace=True)
            estimation_route = estimation_route[["bin_start",
                                                 "tx_route",
                                                 "rx_route"]]

            estimation = pd.merge(estimation_noinfo, estimation_route).set_index("bin_start")
            res = estimation.join(bin_df)

            powertracker = pd.read_csv(pj(folder, "results", "powertracker", "series_powertracker_%.d.csv" % target))
            powertracker["bin_start"] = BIN * (powertracker.time // BIN)

            bin_powertracker = powertracker.groupby("bin_start").max()[["tx", "rx"]]
            for kind in ["tx", "rx"]:
                bin_powertracker["diff_%s" % kind] = bin_powertracker[kind].diff()

            res = res.join(bin_powertracker)
            output_folder = pj(folder, "results", "dashboard")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            res.to_csv(pj(output_folder, "res_%d.csv" % int(target)))
