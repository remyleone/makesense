# coding: utf-8
import pdb
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def _handle_rpl_packet():
	print("Will handle a RPL packet")

def _handle_udp_packet():
	print("Will handle a UDP packet")

estimation_playbook = {
	"udp": _handle_udp_packet,
	"rpl": _handle_rpl_packet
}


def score(known_packets, reference):
	"""
	TODO: This is our evaluation function but it needs to account time criteria and packet type criteria
	"""
	size = lambda x: float(len(x))

	udp_own = lambda x: x[(x.udp_type.notnull()) & (x.mac_src == x.ip_src)]["cumsum"].cumsum()
	udp_forwarding = lambda x: x[(x.udp_type.notnull()) & (x.mac_src != x.ip_src)]["cumsum"].cumsum()
	udp = lambda x: x[(x.udp_type.notnull())]["cumsum"].cumsum()

	res = {
		# General accuracy
		"accuracy": 100 * size(known_packets) / size(reference),

		# Health own
		"reality own applicatif": udp_own(reference) / udp(reference),
		"estimate own applicatif": udp_own(known_packets) / udp(known_packets),

		# Health App
		"reality app": udp(reference) / reference["cumsum"].cumsum(),
		"estimate app": udp(known_packets) / known_packets["cumsum"].cumsum(),

		# Accuracy metrics
		"accuracy own": udp_own(known_packets) / udp_own(reference),
		"accuracy app": udp(known_packets) / udp(reference)

	}
	# TODO: Ajouter une visualisation ici

	fig = plt.figure();
	
	for name, df in res.items():
		if name != "accuracy":
			df.plot(label=name)
	plt.legend()

	


def packets(df_pcap, root="m3-204.grenoble.iot-lab.info", starting_lambda=1):
	"""
	:starting_lambda: In average, how many time does a node needs to repeat a message before it's received
	"""
	df_pcap = df_pcap[df_pcap.mac_src.notnull()]

	pdb.set_trace()

	#score(known_packets, df_pcap)

	# On va utiliser concat pour ajouter des rows a known_packets

	# Pour suivre un paquet a la trace il faut calculer une sorte de hash qui identifie un paquet en cours de transit
	# Il faut repérer un invariant

def revisions(df_pcap, df_serial):
	pdb.set_trace()