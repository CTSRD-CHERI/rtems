#
#  Shared base config file for GEN5200 BSPs
#

include $(RTEMS_ROOT)/make/custom/default.cfg

RTEMS_CPU=powerpc

#  This contains the compiler options necessary to select the CPU model
#  and (hopefully) optimize for it. 
#
CPU_CFLAGS = -mcpu=603e -mstrict-align \
             -meabi -msdata=sysv -fno-common

# optimize flag: typically -O2
CFLAGS_OPTIMIZE_V = -O2 -g -fno-keep-inline-functions
CFLAGS_OPTIMIZE_V += -ffunction-sections -fdata-sections

LDFLAGS = -Wl,--gc-sections
