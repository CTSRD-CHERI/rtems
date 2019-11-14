##
#
# @file
#
# @ingroup mpc55xx_config
#
# @brief Shared configuration file for the MPC55xx board family.
#

include $(RTEMS_ROOT)/make/custom/default.cfg

RTEMS_CPU = powerpc

# FIXME
CPU_CFLAGS = -mcpu=8540 -meabi -msdata=sysv -fno-common -mspe -mabi=spe -mfloat-gprs=single \
    -mstrict-align

CFLAGS_OPTIMIZE_V = -O2 -g -fno-keep-inline-functions
CFLAGS_OPTIMIZE_V += -ffunction-sections -fdata-sections

LDFLAGS = -Wl,--gc-sections
