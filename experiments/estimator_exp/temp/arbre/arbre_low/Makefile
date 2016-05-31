TARGET=sky
CONTIKI=$(HOME)/code//contiki

nodes: udp-client udp-server

run:
	java -jar $(CONTIKI)/tools/cooja/dist/cooja.jar -nogui=main.csc -contiki=$(CONTIKI)

cooja:
	make TARGET=cooja main.csc

push_to_paper:
	cp damier.pdf ~/workspace/tee/img/arbre_traffic_low.pdf

strip_pcap:
	tshark -r output.pcap -Y "frame.time_relative > 50" -w output_stripped.pcap


UIP_CONF_IPV6=1

CFLAGS += -DPROJECT_CONF_H=\"project-conf.h\"


UIP_CONF_IPV6=1
WITH_COMPOWER=1

CFLAGS+= -DUIP_CONF_IPV6_RPL

# Just put a lower than 0 number if you don't want a behavior
CBR_RATE=-1
BATTERY_RATE=-1
RPLINFO_RATE=20
POISSON_RATE=10

CFLAGS+= -lm
CFLAGS+= -DRPLINFO_RATE=$(RPLINFO_RATE)
CFLAGS+= -DBATTERY_RATE=$(BATTERY_RATE)
CFLAGS+= -DCBR_RATE=$(CBR_RATE)
CFLAGS+= -DPOISSON_RATE=$(POISSON_RATE)

ifdef PERIOD
CFLAGS+=-DPERIOD=$(PERIOD)
endif
CFLAGS += -DPROJECT_CONF_H=\"project-conf.h\"
SMALL = 1

ifdef WITH_COMPOWER
APPS+=powertrace
CFLAGS+= -DCONTIKIMAC_CONF_COMPOWER=1 -DWITH_COMPOWER=1
endif

ifdef SERVER_REPLY
CFLAGS+=-DSERVER_REPLY=$(SERVER_REPLY)
endif

include $(CONTIKI)/Makefile.include
