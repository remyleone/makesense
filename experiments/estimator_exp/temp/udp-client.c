#include "contiki.h"
#include "lib/random.h"
#include "sys/ctimer.h"
#include "net/ip/uip.h"
#include "net/ipv6/uip-ds6.h"
#include "net/ip/uip-udp-packet.h"
#include "net/rpl/rpl.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

#define UDP_CLIENT_PORT 8765
#define UDP_SERVER_PORT 5678

#define DEBUG DEBUG_PRINT
#include "net/ip/uip-debug.h"

#define MAX_PAYLOAD_LEN 30

#define UIP_IP_BUF   ((struct uip_ip_hdr *)&uip_buf[UIP_LLH_LEN])

static struct uip_udp_conn *udp_cbr_conn;
static uip_ipaddr_t server_ipaddr;

/**
  "R %s f %d" <= REPLY id FROM node
  "D%d 'H %d'" <= DATA root_id HELLO seq_id
  "B%u" <= BATTERY RATE
  "T%u" <= RPLINFO_REFRESH
  "P%u" <= Preferred parent
  "S%u" <= Exponential Sleep
  "L%u" <= Rate (lambda)
 **/

float poisson_time(float rateParameter)
{
    if (rateParameter != 0.0){
        float u = (float) random_rand() / (float) RANDOM_RAND_MAX;
        float approx_log = u + (u*u)/2.0 + (u*u*u)/3.0; // + (u*u*u*u)/4.0;// + (u*u*u*u*u)/5.0;
        return approx_log / rateParameter;
        //float sleep_time = -log(1.0f - u) / rateParameter; return sleep_time;
    }
    else{
        return -1.0;
    }
}

/*---------------------------------------------------------------------------*/
PROCESS(udp_client_process, "U");
AUTOSTART_PROCESSES(&udp_client_process);
/*---------------------------------------------------------------------------*/
    static void
tcpip_handler(void)
{
    char *str;

    if(uip_newdata()) {
        str = uip_appdata;
        str[uip_datalen()] = '\0';
        PRINTF("Received '%s' from %d\n", str,
                UIP_IP_BUF->srcipaddr.u8[sizeof(UIP_IP_BUF->srcipaddr.u8) - 1]);
    }
}
/*---------------------------------------------------------------------------*/
    static void
send_packet(void *ptr)
{
    static int seq_id;
    char buf[MAX_PAYLOAD_LEN];

    seq_id++;
    PRINTF("DATA send to %d 'H%d'\n",
            server_ipaddr.u8[sizeof(server_ipaddr.u8) - 1], seq_id);
    sprintf(buf, "H%d", seq_id);
    uip_udp_packet_sendto(udp_cbr_conn, buf, strlen(buf),
            &server_ipaddr, UIP_HTONS(UDP_SERVER_PORT));
}

/*---------------------------------------------------------------------------*/
    static void
set_global_address(void)
{
    uip_ipaddr_t ipaddr;

    uip_ip6addr(&ipaddr, 0xaaaa, 0, 0, 0, 0, 0, 0, 0);
    uip_ds6_set_addr_iid(&ipaddr, &uip_lladdr);
    uip_ds6_addr_add(&ipaddr, 0, ADDR_AUTOCONF);

    /* The choice of server address determines its 6LoPAN header compression.
     * (Our address will be compressed Mode 3 since it is derived from our link-local address)
     * Obviously the choice made here must also be selected in udp-server.c.
     *
     * For correct Wireshark decoding using a sniffer, add the /64 prefix to the 6LowPAN protocol preferences,
     * e.g. set Context 0 to aaaa::.  At present Wireshark copies Context/128 and then overwrites it.
     * (Setting Context 0 to aaaa::1111:2222:3333:4444 will report a 16 bit compressed address of aaaa::1111:22ff:fe33:xxxx)
     *
     * Note the IPCMV6 checksum verification depends on the correct uncompressed addresses.
     */

#if 0
    /* Mode 1 - 64 bits inline */
    uip_ip6addr(&server_ipaddr, 0xaaaa, 0, 0, 0, 0, 0, 0, 1);
#elif 1
    /* Mode 2 - 16 bits inline */
    uip_ip6addr(&server_ipaddr, 0xaaaa, 0, 0, 0, 0, 0x00ff, 0xfe00, 1);
#else
    /* Mode 3 - derived from server link-local (MAC) address */
    uip_ip6addr(&server_ipaddr, 0xaaaa, 0, 0, 0, 0x0250, 0xc2ff, 0xfea8, 0xcd1a); //redbee-econotag
#endif
}
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(udp_client_process, ev, data)
{
    PROCESS_BEGIN();

    PROCESS_PAUSE();

    #if CBR_RATE > 0
    PRINTF("CBR RATE %d\n", (uint16_t) CBR_RATE);
    static struct stimer udp_cbr_timer;
    stimer_set(&udp_cbr_timer, (uint16_t) CBR_RATE + random_rand() / 1000);
    #endif

    #if POISSON_RATE > 0
    PRINTF("POISSON RATE %d\n", (uint16_t) POISSON_RATE);
    static struct stimer udp_poisson_timer;
    stimer_set(&udp_poisson_timer, poisson_time(POISSON_RATE) + random_rand() / 1000);
    #endif

    #if BATTERY_RATE > 0
    PRINTF("BATTERY RATE%u\n", (uint16_t) BATTERY_RATE);
    static struct stimer battery_timer;
    stimer_set(&battery_timer, (uint16_t) BATTERY_RATE);
    #endif

    #if RPLINFO_RATE > 0
    PRINTF("RPLINFO RATE %u\n", (uint16_t) RPLINFO_RATE);
    static struct stimer rplinfo_timer;
    stimer_set(&rplinfo_timer, (uint16_t) RPLINFO_RATE);
    #endif

    set_global_address();

    // UDP CBR SOCKET
    udp_cbr_conn = udp_new(NULL, UIP_HTONS(UDP_SERVER_PORT), NULL);
    if(udp_cbr_conn == NULL) {
        PROCESS_EXIT();
    }
    udp_bind(udp_cbr_conn, UIP_HTONS(UDP_CLIENT_PORT));

    while(1) {

        PROCESS_PAUSE();

        if(ev == tcpip_event) {
            tcpip_handler();
        }

        #if POISSON_RATE > 0
        if(stimer_expired(&udp_poisson_timer)) {
            send_packet(NULL);
            stimer_set(&udp_poisson_timer, poisson_time(POISSON_RATE));
            stimer_restart(&udp_poisson_timer);
            stimer_reset(&udp_poisson_timer);
        }
        #endif

        #if CBR_RATE > 0
        if(stimer_expired(&udp_cbr_timer)) {
            send_packet(NULL);
            stimer_set(&udp_cbr_timer, CBR_RATE);
            stimer_restart(&udp_cbr_timer);
            stimer_reset(&udp_cbr_timer);
        }
        #endif

        #if RPLINFO_RATE > 0
        if(stimer_expired(&rplinfo_timer)) {
            PRINTF("Preferred Parent %u\n",
                    (int) rpl_get_parent_ipaddr((rpl_parent_t *) rpl_get_any_dag()->preferred_parent)->u8[sizeof(uip_ipaddr_t)-1]);
            //uip_udp_packet_sendto(udp_cbr_conn, "R", strlen("R"),
            //        &server_ipaddr, UIP_HTONS(UDP_CLIENT_PORT));
            stimer_reset(&rplinfo_timer);
        }
        #endif

        #if BATTERY_RATE > 0
        if(stimer_expired(&battery_timer)) {
            PRINTF("Battery recalibration\n");
            uip_udp_packet_sendto(udp_cbr_conn, "B", strlen("B"), &server_ipaddr, UIP_HTONS(UDP_CLIENT_PORT));
            stimer_reset(&battery_timer);
        }
        #endif

    }

    PROCESS_END();
}
