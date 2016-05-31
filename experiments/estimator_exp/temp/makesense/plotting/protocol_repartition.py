import pdb
from collections import defaultdict
import pandas as pd
from os.path import join as pj
import matplotlib.pyplot as plt
import os

BIN = 25


def plot_protocol_repartition_depth(folder):
    output_folder = pj(folder, "results", "protocol_repartition")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))
    depth_df.set_index("node", inplace=True)

    pcap_df = pd.read_csv(pj(folder, "results", "pcap_relooked.csv"))
    pcap_df = pcap_df.join(depth_df, on="mac_src")

    res = pd.DataFrame()

    res["rpl"] = pcap_df[pcap_df.icmpv6_type == "rpl"].groupby("depth").sum().length
    res["udp"] = pcap_df[pcap_df.icmpv6_type == "udp"].groupby("depth").sum().length

    RATE = 250000
    res["rpl"] = 8.0 * res["rpl"] / RATE
    res["udp"] = 8.0 * res["udp"] / RATE

    ax = res.plot(kind="bar", stacked=True)
    ax.set_ylabel('Time by protocol [s]')
    ax.set_xlabel("Depth")
    ax.set_xticklabels(res.index, rotation=0)

    fig = plt.gcf()
    plt.tight_layout()

    # fig.set_size_inches(18.5, 10.5)
    fig.savefig(pj(output_folder, 'protocol_repartition_depth.pdf'), format="pdf")
    plt.close('all')


def plot_protocol_repartition(folder):
    output_folder = pj(folder, "results", "protocol_repartition")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))
    targets = depth_df.node.unique()

    for target in targets:
        df = pd.read_csv(pj(output_folder, 'protocol_repartition_%d.csv' % target))
        df.set_index("bin_start", inplace=True)
        ax = df.plot(kind="bar")
        ax.set_ylabel('Time by protocol [s]')
        ax.set_xlabel("Time [s]")
        ax.set_ylim([0.0, df.max().max() * 1.5])
        ax.set_xticklabels(df.index.map(int), rotation=0)
        # pdb.set_trace()

        fig = plt.gcf()
        plt.legend(ncol=2)
        plt.tight_layout()
        # fig.set_size_inches(18.5, 10.5)
        fig.savefig(pj(output_folder, "protocol_repartition_%d.pdf" % target), format="pdf")
        plt.close('all')

# def io2csv(folder):
#     """
#     """
#     input_path = pj(folder, "io.log")
#     output_path = pj(folder, "io.csv")
#     with open(input_path) as input_file, open(output_path, "w") as csv_out:
#         fields = ["bin_start", "bin_end", "total_bytes",
#                   "udp_bytes", "rpl_bytes", "ping_bytes", "coap_bytes",
#                   "battery_bytes", "rplinfo_bytes"]
#         writer = DictWriter(csv_out, delimiter=",", fieldnames=fields)
#         writer.writeheader()
#         result = []
#         for line in input_file:
#             if "<>" in line:
#                 split_line = line.split("|")
#                 d = {"bin_start": float(split_line[1].split("<>")[0]),
#                      "bin_end": float(split_line[1].split("<>")[1]),
#                      "total_bytes": float(split_line[3]),
#                      "udp_bytes": float(split_line[5]),
#                      "rpl_bytes": float(split_line[7]),
#                      "ping_bytes": float(split_line[9]),
#                      "coap_bytes": float(split_line[11]),
#                      "battery_bytes": float(split_line[13]),
#                      "rplinfo_bytes": float(split_line[15])}
#                 result.append(d)
#                 writer.writerow(d)
#         return result


# def pcap_stats(stat, output_path):
#     with open(output_path, "w") as output_file:
#         command = ["tshark", "-q",
#                    "-z", stat,
#                    "-r", pj(folder, "output.pcap")]
#         print(str(command))
#         process = subprocess.Popen(command, stdout=subprocess.PIPE)
#         stdout, stderr = process.communicate()
#         output_file.write(stdout)
#         return stdout


# def io(folder):
#     log_file = pj(folder, "io.log")
#     stat = ["io", "stat", str(BINS), "udp", "icmpv6.type==155",
#             "icmpv6.type==128||icmpv6.type==129", "coap",
#             "data.data == 42",
#             "data.data == 52"]
#     # RPL packets
#     # ICMPV6 PING PACKETS
#     pcap_stats(
#         stat=",".join(stat),
#         output_path=log_file)


# def repartition_protocol(folder):
#     """
#     Representation of protocol repartition (stacked histogram)

#     Include UDP, CoAP, ping, RPL, other...
#     """
#     fig1 = plt.figure()
#     ax1 = fig1.add_subplot(111)
#     ax1.set_title("Protocol repartition")
#     ax1.set_ylabel("KBytes")
#     ax1.set_xlabel("Time (s)")
#     ax1.set_ylim([0, 120])

#     color = {"coap": "red",
#              "rpl": "blue",
#              "ping": "green",
#              "total": "black",
#              "udp": "yellow",
#              "rplinfo": "cyan",
#              "battery": "magenta"}

#     with open(pj(folder, "io.csv")) as f:
#         reader = DictReader(f)

#         # Hack to avoid duplicate label in legend
#         label_first = {"total": True, "rpl": True, "ping": True,
#                        "udp": True, "coap": True, "battery": True,
#                        "rplinfo": True}
#         for row in reader:
#             row = {k: float(v) for k, v in row.iteritems()}
#             row["bin_end"] /= 5.0
#             row["bin_start"] /= 5.0
#             for kind in ["rpl_bytes", "udp_bytes", "rplinfo_bytes"]:
#                 row[kind] /= 1000
#             width = (row["bin_end"] - row["bin_start"]) / 2
#             bottom = 0.0

#             # rpl
#             if row["rpl_bytes"]:
#                 ax1.bar(row["bin_start"] + width, row["rpl_bytes"],
#                         color=color["rpl"], hatch="//", width=width, bottom=bottom,
#                         label="RPL" if label_first["rpl"] else "")
#                 bottom += row["rpl_bytes"]
#                 label_first["rpl"] = False

#             # udp
#             if row["udp_bytes"]:
#                 ax1.bar(row["bin_start"] + width, row["udp_bytes"],
#                         color=color["udp"], width=width, bottom=bottom,
#                         label='UDP' if label_first["udp"] else "")
#                 bottom += row["udp_bytes"]
#                 label_first["udp"] = False

#             # rplinfo
#             if row["rplinfo_bytes"]:
#                 ax1.bar(row["bin_start"] + width, row["rplinfo_bytes"],
#                         color=color["rplinfo"], width=width, bottom=bottom,
#                         label="rplinfo" if label_first["rplinfo"] else "")
#                 # Last value
#                 #bottom += row["rplinfo_bytes"]
#                 label_first["rplinfo"] = False

#     key, value = [], []
#     for k, v in color.items():
#         key.append(k)
#         value.append(v)
#     #plt.legend(tuple(key), tuple(value))
#     plt.legend(loc='best')
#     format_axes(ax1)
#     plt.tight_layout()
#     plt.savefig(pj(folder, "repartition_protocol.pdf"),
#                 format="pdf")
