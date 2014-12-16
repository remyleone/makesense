#include <stdio.h>
#include "contiki.h"

static int my_value = {{ my_value }};

/*---------------------------------------------------------------------------*/
PROCESS(dummy_hello_world_process, "Hello world process");
AUTOSTART_PROCESSES(&dummy_hello_world_process);
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(dummy_hello_world_process, ev, data)
{
  PROCESS_BEGIN();

  while(1) {
    printf("Hello, world. My value is %d\n", my_value);
  }

  PROCESS_END();
}
/*---------------------------------------------------------------------------*/