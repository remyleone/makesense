// MAC layer
#undef NETSTACK_CONF_MAC
#define NETSTACK_CONF_MAC csma_driver
#undef NETSTACK_CONF_RDC
#define NETSTACK_CONF_RDC contikimac_driver
//#undef UIP_ND6_RETRANS_TIMER
//#define UIP_ND6_RETRANS_TIMER 999999999
// phase optimization should be set to 1. it keeps track of phases of the neighbors
#undef CONTIKIMAC_CONF_WITH_PHASE_OPTIMIZATION
#define CONTIKIMAC_CONF_WITH_PHASE_OPTIMIZATION 1
#undef WITH_PHASE_OPTIMIZATION
#define WITH_PHASE_OPTIMIZATION 1

// set to 1 to enable downward traffic from the sink to the nodes. data is sent by the sink periodically
// Just put a lower than 0 number if you don't want a behavior
#undef CBR_RATE
#define CBR_RATE -1
#undef BATTERY_RATE
#define BATTERY_RATE -1
#undef SERVER_REPLY
#define SERVER_REPLY 0
#undef RPLINFO_RATE
#define RPLINFO_RATE 5
#undef POISSON_RATE
#define POISSON_RATE 10

// Size of the packet message
#undef SIZE
#define SIZE 10

// set to 1 to estimate energy consumption on the node
#define WITH_COMPOWER 1
