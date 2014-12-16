#include <stdio.h>
#include "contiki.h"
#include "sys/stimer.h"

static struct stimer periodic;
static int my_value = {{ my_value }};

/*---------------------------------------------------------------------------*/
PROCESS(dummy_hello_world_process, "Hello world process");
AUTOSTART_PROCESSES(&dummy_hello_world_process);
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(dummy_hello_world_process, ev, data)
{
  PROCESS_BEGIN();

  stimer_set(&periodic, 5);

  while(1) {

    PROCESS_YIELD();

    printf("Hello, world. My value is %d\n", my_value);
    stimer_reset(&periodic);
  }

  PROCESS_END();
}
/*---------------------------------------------------------------------------*/
