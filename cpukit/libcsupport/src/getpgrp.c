#if HAVE_CONFIG_H
#include "config.h"
#endif

#include <unistd.h>
#include <rtems.h>

/*
 *  4.3.1 Get Process Group IDs, P1003.1b-1993, p. 89
 */

pid_t getpgrp( void )
{
  /*
   *  This always succeeds and returns the process group id.  For rtems,
   *  this will always be the local node;
   */

  return rtems_object_get_local_node();
}
