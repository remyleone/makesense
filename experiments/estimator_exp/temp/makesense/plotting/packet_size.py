#!/usr/bin/env python3

from matplotlib import pyplot as plt
from csv import DictReader

payload_size, tx_sender, rx_sender, tx_receiver, rx_receiver = [], [], [], [], []
with open("calibration_contikimac.csv") as f:
    reader = DictReader(f)
    for row in reader:
        payload_size.append(float(row["payload_size"]))
        tx_sender.append(float(row["tx_sender"]))
        rx_sender.append(float(row["rx_sender"]))
        tx_receiver.append(float(row["tx_receiver"]))
        rx_receiver.append(float(row["rx_receiver"]))

plt.plot(payload_size, tx_sender, "o-", label="tx_sender")
plt.plot(payload_size, rx_sender, "o-", label="rx_sender")
plt.plot(payload_size, tx_receiver, "o-", label="tx_receiver")
plt.plot(payload_size, rx_receiver, "o-", label="rx_receiver")
plt.title("TX & RX by payload")
plt.xlabel("Payload size [bytes]")
plt.xlim(10, 90)
plt.ylabel("Average time for treating a message [s]")
plt.legend(loc=2)
plt.savefig("packet_size.pdf", format="pdf")
plt.show()
