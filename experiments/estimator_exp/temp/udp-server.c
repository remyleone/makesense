#include "contiki.h"
#include "contiki-lib.h"
#include "contiki-net.h"
#include "net/ip/uip.h"
#include "net/rpl/rpl.h"
#include "net/ipv6/uip-ds6.h"
//#include "net/netstack.h"
#if PLATFORM_HAS_BUTTON
#include "dev/button-sensor.h"
#endif /* PLATFORM_HAS_BUTTON */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define DEBUG DEBUG_PRINT
#include "net/ip/uip-debug.h"

#define UIP_IP_BUF   ((struct uip_ip_hdr *)&uip_buf[UIP_LLH_LEN])

#define UDP_CLIENT_PORT	8765
#define UDP_SERVER_PORT	5678

#ifndef PERIOD
#define PERIOD 60
#endif

#ifndef START_INTERVAL
#define START_INTERVAL		(60 * CLOCK_SECOND)
#endif

#define SEND_INTERVAL		(PERIOD * CLOCK_SECOND)
#define SEND_TIME		(random_rand() % (SEND_INTERVAL))
#define MAX_PAYLOAD_LEN		30

#define MAX_SENDERS			50

static struct uip_udp_conn *server_conn;
typedef struct sender_id {
    int id;
    int counter;
} sender_id_t;

static sender_id_t senders[MAX_SENDERS];
static int current_dest;

PROCESS(udp_server_process, "UDP server process");
AUTOSTART_PROCESSES(&udp_server_process);
/*---------------------------------------------------------------------------*/
    static void
sender_list_init()
{
    uint8_t i;

    for(i = 0; i < MAX_SENDERS; i++){
        senders[i].id = 0;
        senders[i].counter = 0;
    }
}

    static void
print_routes()
{
    static uip_ds6_route_t *r;
    //static uip_ds6_nbr_t *nbr;

    /*PRINTF("Neighbors: ");
      for(nbr = nbr_table_head(ds6_neighbors);
      nbr != NULL;
      nbr = nbr_table_next(ds6_neighbors, nbr)) {
      PRINTF(" %u", (uint8_t) nbr->ipaddr.u8[sizeof(uip_ipaddr_t)-1]);
      }
      PRINTF("\n");*/

    for(r = uip_ds6_route_head(); r != NULL; r = uip_ds6_route_next(r)) {
        PRINTF("route: %u", (uint8_t) r->ipaddr.u8[sizeof(uip_ipaddr_t)-1]);
        PRINTF(" via %u\n", (uint8_t) uip_ds6_route_nexthop(r)->u8[sizeof(uip_ipaddr_t)-1]);
    }
}
/*---------------------------------------------------------------------------*/
    static void
insert_sender(int s)
{
    int i;
    int insert = 0;

    for(i = 0; i < MAX_SENDERS; i++){
        if(senders[i].id == s){
            //PRINTF("Sender already in the list\n");
            return;
        } else if(senders[i].id == 0){
            insert = 1;
            break;
        }
    }
    if(insert == 1){
        senders[i].id = s;
        //senders[i].counter = 0;
        //PRINTF("Inserted node %d, at pos %d\n", s, i);
    } else {
        //		PRINTF("list full\n");
    }
    //	print_sender_list();
}
/*---------------------------------------------------------------------------*/
    static void
tcpip_handler(void)
{
    char *appdata;
    uint8_t src;

    if(uip_newdata()) {
        appdata = (char *)uip_appdata;
        appdata[uip_datalen()] = 0;
        PRINTF("DATA recv '%s' from ", appdata);
        PRINTF("%d",
                UIP_IP_BUF->srcipaddr.u8[sizeof(UIP_IP_BUF->srcipaddr.u8) - 1]);
        PRINTF("\n");
        src = UIP_IP_BUF->srcipaddr.u8[sizeof(UIP_IP_BUF->srcipaddr.u8) - 1];
        insert_sender(src);
    }
}
/*---------------------------------------------------------------------------*/
uip_ipaddr_t build_ipv6_addr(uint8_t id)
{
    uip_ipaddr_t ip_addr;
    uip_ds6_addr_t * global;
    uint8_t i;

    global = uip_ds6_get_global(ADDR_PREFERRED);
    for(i = 0; i < 16; i++)
        ip_addr.u8[i] = global->ipaddr.u8[i];
    ip_addr.u8[11] = id;
    ip_addr.u8[13] = id;
    ip_addr.u8[14] = id;
    ip_addr.u8[15] = id;

    return ip_addr;
}
/********************************************************************************/
    static void
send_packet(void *ptr)
{
    uip_ipaddr_t dest_addr;
    int i;
    //	static int seq_id;
    char buf[MAX_PAYLOAD_LEN];

    //	seq_id++;
    if(current_dest >= MAX_SENDERS || senders[current_dest].id == 0){
        current_dest = 0;
    }

    if(senders[current_dest].id != 0){
        dest_addr = build_ipv6_addr(senders[current_dest].id);
        PRINTF("REPLY send to %d 'Reply %d'\n", senders[current_dest].id, ++senders[current_dest].counter);
        uip_ipaddr_copy(&server_conn->ripaddr, &dest_addr);
        sprintf(buf, "Reply %d", senders[current_dest].counter);
        uip_udp_packet_send(server_conn, buf, strlen(buf));
        uip_create_unspecified(&server_conn->ripaddr);
    }
    //	print_sender_list();
}
/*static void
  print_local_addresses(void)
  {
  int i;
  uint8_t state;

  PRINTF("Server IPv6 addresses: ");
  for(i = 0; i < UIP_DS6_ADDR_NB; i++) {
  state = uip_ds6_if.addr_list[i].state;
  if(state == ADDR_TENTATIVE || state == ADDR_PREFERRED) {
  PRINT6ADDR(&uip_ds6_if.addr_list[i].ipaddr);
  PRINTF("\n");
  hack to make address "final"
  if (state == ADDR_TENTATIVE) {
  uip_ds6_if.addr_list[i].state = ADDR_PREFERRED;
  }
  }
  }
  }*/
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(udp_server_process, ev, data)
{
    uip_ipaddr_t ipaddr;
    struct uip_ds6_addr *root_if;
    static struct etimer periodic;
    static struct ctimer backoff_timer;

    PROCESS_BEGIN();

    PROCESS_PAUSE();

#if PLATFORM_HAS_BUTTON
    SENSORS_ACTIVATE(button_sensor);
#endif /* PLATFORM_HAS_BUTTON */

    //  PRINTF("UDP server started\n");

#if UIP_CONF_ROUTER
    /* The choice of server address determines its 6LoPAN header compression.
     * Obviously the choice made here must also be selected in udp-client.c.
     *
     * For correct Wireshark decoding using a sniffer, add the /64 prefix to the 6LowPAN protocol preferences,
     * e.g. set Context 0 to aaaa::.  At present Wireshark copies Context/128 and then overwrites it.
     * (Setting Context 0 to aaaa::1111:2222:3333:4444 will report a 16 bit compressed address of aaaa::1111:22ff:fe33:xxxx)
     * Note Wireshark's IPCMV6 checksum verification depends on the correct uncompressed addresses.
     */

#if 0
    /* Mode 1 - 64 bits inline */
    uip_ip6addr(&ipaddr, 0xaaaa, 0, 0, 0, 0, 0, 0, 1);
#elif 1
    /* Mode 2 - 16 bits inline */
    uip_ip6addr(&ipaddr, 0xaaaa, 0, 0, 0, 0, 0x00ff, 0xfe00, 1);
#else
    /* Mode 3 - derived from link local (MAC) address */
    uip_ip6addr(&ipaddr, 0xaaaa, 0, 0, 0, 0, 0, 0, 0);
    uip_ds6_set_addr_iid(&ipaddr, &uip_lladdr);
#endif

    uip_ds6_addr_add(&ipaddr, 0, ADDR_MANUAL);
    root_if = uip_ds6_addr_lookup(&ipaddr);
    if(root_if != NULL) {
        rpl_dag_t *dag;
        dag = rpl_set_root(RPL_DEFAULT_INSTANCE,(uip_ip6addr_t *)&ipaddr);
        uip_ip6addr(&ipaddr, 0xaaaa, 0, 0, 0, 0, 0, 0, 0);
        rpl_set_prefix(dag, &ipaddr, 64);
        PRINTF("created a new RPL dag\n");
    } else {
        PRINTF("failed to create a new RPL DAG\n");
    }
#endif /* UIP_CONF_ROUTER */

    //  print_local_addresses();

    /* The data sink runs with a 100% duty cycle in order to ensure high
       packet reception rates. */
    NETSTACK_MAC.off(1);

    server_conn = udp_new(NULL, UIP_HTONS(UDP_CLIENT_PORT), NULL);
    if(server_conn == NULL) {
        //    PRINTF("No UDP connection available, exiting the process!\n");
        PROCESS_EXIT();
    }
    udp_bind(server_conn, UIP_HTONS(UDP_SERVER_PORT));
    sender_list_init();

    current_dest = 0;
    etimer_set(&periodic, START_INTERVAL);

    while(1) {
        PROCESS_YIELD();
        if(ev == tcpip_event) {
            tcpip_handler();
#if PLATFORM_HAS_BUTTON
        } else if (ev == sensors_event && data == &button_sensor) {
            PRINTF("Initiating global repair\n");
            rpl_repair_root(RPL_DEFAULT_INSTANCE);
#endif /* PLATFORM_HAS_BUTTON */
        }
        else if (etimer_expired(&periodic)) {
            etimer_set(&periodic, SEND_INTERVAL);
#if SERVER_REPLY
            // current_dest is a counter used to send packets to each node sequentially
            current_dest++;
            ctimer_set(&backoff_timer, SEND_TIME, send_packet, NULL);
#endif
            print_routes();
        }
    }

    PROCESS_END();
}
/*---------------------------------------------------------------------------*/
