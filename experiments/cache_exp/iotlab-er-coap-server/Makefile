CONTIKI_PROJECT=er-example-server

all: $(CONTIKI_PROJECT) 

# variable for this Makefile
# configure CoAP implementation (3|7|12|13) (er-coap-07 also supports CoAP draft 08)
WITH_COAP=13

# border-router port
PORT ?= 0

CONTIKI=../../..

UIP_CONF_IPV6=1
CFLAGS += -DUIP_CONF_IPV6=1
CFLAGS+= -DUIP_CONF_IPV6_RPL=1
CFLAGS += -DUIP_CONF_BUFFER_SIZE=1024

#linker optimizations
SMALL=1

CFLAGS += -DPROJECT_CONF_H=\"project-conf.h\"
#PROJECT_SOURCEFILES += sensors-collecting.c

ifeq ($(WITH_COAP), 13)
${info INFO: compiling with CoAP-13}
CFLAGS += -DWITH_COAP=13
CFLAGS += -DREST=coap_rest_implementation
CFLAGS += -DUIP_CONF_TCP=0
APPS += er-coap-13
endif

APPS += erbium

include $(CONTIKI)/Makefile.include
