def time_per_message(tx, rx, ms):
    res = {}
    with open("calibration.csv", "w") as f:
        writer = DictWriter(f, fieldnames=["payload_size", "tx_sender", "rx_sender", "tx_receiver", "rx_receiver"])
        writer.writeheader()
        for size in sizes:
            serial_path = ("/").join([str(size), "serial.log"])
            p_path = ("/").join([str(size), "powertracker_stripped.csv"])
            if ms[serial_path]:
                writer.writerow({"payload_size": size,
                    "tx_sender": tx[p_path]["sender"] / ms[serial_path],
                    "rx_sender": rx[p_path]["sender"] / ms[serial_path],
                    "tx_receiver": tx[p_path]["receiver"] / ms[serial_path],
                    "rx_receiver": rx[p_path]["receiver"] / ms[serial_path]})


def time_per_message(tx, rx, ms):
    folders = ["%s/%d" % (kind, size) for (kind, size) in product(kinds, sizes)]
    for kind in kinds:
        avg_rx_receiver, avg_rx_sender, avg_tx_receiver, avg_tx_sender = [], [], [], []
        for size in sizes:
            serial_path = ("/").join([kind, str(size), "serial.log"])
            p_path = ("/").join([kind, str(size), "powertracker_stripped.csv"])
            if ms[serial_path]:
                avg_tx_sender.append(tx[p_path]["sender"] / ms[serial_path])
                avg_tx_receiver.append(tx[p_path]["receiver"] / ms[serial_path])
                avg_rx_sender.append(rx[p_path]["sender"] / ms[serial_path])
                avg_rx_receiver.append(rx[p_path]["receiver"] / ms[serial_path])
                #print("AVG(TX/msg)(SENDER) for %d => %f" % (size, avg_tx_sender))
                #print("AVG(TX/msg)(RECEIVER) for %d => %f" % (size, avg_tx_receiver))
                #print("AVG(RX/msg)(SENDER) for %d => %f" % (size, avg_rx_sender))
                #print("AVG(RX/msg)(RECEIVER) for %d => %f" % (size, avg_rx_receiver))
            else:
                avg_tx_sender.append(None)
                avg_tx_receiver.append(None)
                avg_rx_sender.append(None)
                avg_rx_receiver.append(None)

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title("tx per message for %s" % kind)
        ax1.set_xlabel("Size of payload")
        ax1.set_ylabel("TX_TIME/#messages")
        print(avg_rx_sender)
        ax1.plot(sizes, avg_tx_sender, label="tx sender")
        ax1.plot(sizes, avg_rx_sender, label="rx sender")
        ax1.plot(sizes, avg_tx_receiver, label="tx receiver")
        ax1.plot(sizes, avg_rx_receiver, label="rx receiver")

        ax1.legend()
        fig.savefig("%s.pdf" % kind, format="pdf")

time_per_message(tx, rx, ms)
