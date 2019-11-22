#!/usr/bin/env python3

# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (C) 2019 embedded brains GmbH
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import re

families = {}

archs = [
"arm",
"bfin",
"epiphany",
"i386",
"lm32",
"m68k",
"mips",
"moxie",
"nios2",
"or1k",
"powerpc",
"riscv",
"sh",
"sparc",
"sparc64",
"v850",
"x86_64",
]


enable_map = {
"HAS_MP": "RTEMS_MULTIPROCESSING",
"HAS_NETWORKING": "RTEMS_NETWORKING",
"HAS_SMP": "RTEMS_SMP",
"QEMU": "qemuprep",
"shared": "armcortexa9",
}

enable_is_option = {
"ENABLE_LCD": "ENABLE_LCD",
"ENABLE_UMON_CONSOLE": "ENABLE_UMON_CONSOLE",
"ENABLE_UMON": "ENABLE_UMON",
"HAS_IDE": "BSP_ENABLE_IDE",
"RTEMS_VGA": "BSP_ENABLE_VGA",
"USE_VBE_RM": "USE_VBE_RM",
"USE_CIRRUS_GD5446": "USE_CIRRUS_GD5446",
"USE_VGA": "USE_VGA",
"TMS570_USE_HWINIT_STARTUP": "TMS570_USE_HWINIT_STARTUP",
}

enable_by_to_obj = {
"enabled-by:\n- and:\n  - qemuprep\n  - RTEMS_NETWORKING": "QEMUNET",
"enabled-by:\n- and:\n  - RTEMS_NETWORKING\n  - not: RTEMS_SMP": "NETNOSMP",
"enabled-by:\n- and:\n  - RTEMS_VGA\n  - USE_CIRRUS_GD5446": "VGACIR",
"enabled-by:\n- and:\n  - RTEMS_VGA\n  - USE_VBE_RM": "VGAVBE",
"enabled-by:\n- and:\n  - RTEMS_VGA\n  - USE_VGA": "VGAVGA",
"enabled-by:\n- armcortexa9": "A9",
"enabled-by:\n- ENABLE_LCD": "LCD",
"enabled-by:\n- ENABLE_UMON": "UMON",
"enabled-by:\n- ENABLE_UMON_CONSOLE": "UMONCON",
"enabled-by:\n- HAS_IDE": "IDE",
"enabled-by:\n- RTEMS_MULTIPROCESSING": "MPCI",
"enabled-by:\n- RTEMS_NETWORKING": "NET",
"enabled-by:\n- RTEMS_SMP": "SMP",
"enabled-by:\n- RTEMS_VGA": "VGA",
"enabled-by:\n- TMS570_USE_HWINIT_STARTUP": "HWINIT",
}

make_include_to_uid = {
"bsps/bfin/shared/shared-sources.am": "RTEMS-BUILD-BSP-BFIN-OBJ",
"bsps/m68k/shared/fpsp-sources.am": "RTEMS-BUILD-BSP-M68K-OBJFPSP",
"bsps/powerpc/shared/exceptions-sources.am": "RTEMS-BUILD-BSP-POWERPC-OBJEXC",
"bsps/powerpc/shared/shared-sources.am": "RTEMS-BUILD-BSP-POWERPC-OBJ",
"bsps/powerpc/shared/vme-sources.am": "RTEMS-BUILD-BSP-POWERPC-OBJVME",
"bsps/shared/grlib-sources.am": "RTEMS-BUILD-BSP-OBJGRLIB",
"bsps/shared/irq-default-sources.am": "RTEMS-BUILD-BSP-OBJIRQDFLT",
"bsps/shared/irq-sources.am": "RTEMS-BUILD-BSP-OBJIRQ",
"bsps/shared/shared-sources.am": "RTEMS-BUILD-BSP-OBJ",
}

tcfg_include_to_uid = {
"testdata/disable-iconv-tests.tcfg": "RTEMS-BUILD-BSP-TSTNOICONV",
"testdata/disable-intrcritical-tests.tcfg": "RTEMS-BUILD-BSP-TSTNOINTRCRIT",
"testdata/disable-jffs2-tests.tcfg": "RTEMS-BUILD-BSP-TSTNOJFFS2",
"testdata/disable-libdl-tests.tcfg": "RTEMS-BUILD-BSP-TSTNOLIBDL",
"testdata/disable-mrfs-tests.tcfg": "RTEMS-BUILD-BSP-TSTNORFS",
"testdata/require-tick-isr.tcfg": "RTEMS-BUILD-BSP-TSTREQTICK",
"testdata/small-memory-testsuite.tcfg": "RTEMS-BUILD-BSP-TSTSMALLMEM",
}

option_to_uid = {
"ALLOW_IRQ_NESTING": "OPTENIRQNEST",
"ARM_GENERIC_TIMER_FREQ": "OPTGENTMRFREQ",
"ARM_GENERIC_TIMER_UNMASK_AT_TICK": "OPTGENTNUNMASK",
"ARM_GENERIC_TIMER_USE_VIRTUAL": "OPTGENTMRUSEVIRT",
"ARM_LPC1768": "OPTLPC1768",
"ARM_MMU_USE_SMALL_PAGES": "OPTMMUSMALLPAGES",
"ARM_TMS570LS3137": "OPTTMS570LS3137",
"BSP_START_ZIMAGE_HEADER": "OPTZIMGHDR",
"BSP_XEN_RAM_LENGTH": "OPTRAMLEN",
"BSP_XEN_NOCACHE_LENGTH": "OPTNOCACHELEN",
"BSP_XEN_RAM_BASE": "OPTRAMBASE",
"BSP_XEN_LOAD_OFFSET": "OPTLOADOFF",
"BSP_XEN_MMU_LENGTH": "OPTMMULEN",
"ATSAM_CHANGE_CLOCK_FROM_SRAM": "OPTCHGCLKSRAM",
"ATSAM_CONSOLE_BAUD": "OPTCONBAUD",
"ATSAM_CONSOLE_DEVICE_INDEX": "OPTCONIDX",
"ATSAM_CONSOLE_DEVICE_TYPE": "OPTCONTYPE",
"ATSAM_CONSOLE_USE_INTERRUPTS": "OPTCONIRQ",
"ATSAM_MCK": "OPTMCK",
"ATSAM_SLOWCLOCK_USE_XTAL": "OPTUSEXTAL",
"BBB_DEBUG": "OPTDEBUG",
"BENCHMARK_IRQ_PROCESSING": "OPTBENCHIRQ",
"BFIN_ON_SKYEYE": "OPTSKYEYE",
"BOARD_MAINOSC": "OPTOSCMAIN",
"BSP_ARM_A9MPCORE_PERIPHCLK": "OPTA9PERIPHCLK",
"BSP_CONSOLE_BAUD": "OPTCONBAUD",
"BSP_CONSOLE_MINOR": "OPTCONMINOR",
"BSP_CPU_CLOCK_SPEED": "OPTCPUCLK",
"BSP_DATA_CACHE_ENABLED": "OPTCACHEDATA",
"BSP_DATA_CACHE_USE_WRITE_THROUGH": "OPTCACHEWRITETHRU",
"BSP_DEFAULT_BAUD_RATE": "OPTCONBAUD",
"BSP_ENABLE_COM1_COM4": "OPTENCOM14",
"BSP_ENABLE_IDE": "OPTENIDE",
"BSP_ENABLE_VGA": "OPTENVGA",
"BSP_EPIPHANY_PERIPHCLK": "OPTPERIPHCLK",
"BSP_FDT_BLOB_COPY_TO_READ_ONLY_LOAD_AREA": "OPTFDTCPYRO",
"BSP_FDT_BLOB_READ_ONLY": "OPTFDTRO",
"BSP_FDT_BLOB_SIZE_MAX": "OPTFDTMXSZ",
"BSP_FDT_IS_SUPPORTED": "OPTFDTEN",
"BSP_GDB_STUB": "OPTGDBSTUB",
"BSP_GENERIC_OR1K_PERIPHCLK": "OPTPERIPHCLK",
"BSP_GPIOPCR_INITMASK": "OPTGPIOMSK",
"BSP_GPIOPCR_INITVAL": "OPTGPIOVAL",
"BSP_HAS_RM52xx": "OPTRM52XX",
"BSP_HAS_TX49xx": "OPTTX49XX",
"BSP_HAS_USC320": "OPTUSC320",
"BSP_INSTRUCTION_CACHE_ENABLED": "OPTCACHEINST",
"BSP_INTERRUPT_HANDLER_TABLE_SIZE": "OPTIRQTBLSZ",
"BSP_IS_RPI2": "OPTRPI2",
"BSP_LEON3_SMP": "OPTLEON3SMP",
"BSP_MINIMUM_TASK_STACK_SIZE": "OPTMINTSKSTKSZ",
"BSP_POWER_DOWN_AT_FATAL_HALT": "OPTPWRDWNHLT",
"BSP_START_COPY_FDT_FROM_U_BOOT": "OPTFDTUBOOT",
"BSP_START_IN_HYP_SUPPORT": "OPTENHYP",
"BSP_START_NEEDS_REGISTER_INITIALIZATION": "OPTREGINIT",
"BSP_START_RESET_VECTOR": "OPTRESETVEC",
"BSP_UART_AVAIL_MASK": "OPTUARTMSK",
"BSP_USB_EHCI_MPC83XX_HAS_ULPI": "OPTULPI",
"BSP_USB_OTG_TRANSCEIVER_I2C_ADDR": "OPTOTGI2C",
"BSP_USB_OTG_TRANSCEIVER_VBUS": "OPTOTGVBUS",
"BSP_USE_DATA_CACHE_BLOCK_TOUCH": "OPTCACHEBLKTOUCH",
"BSP_USE_NETWORK_FEC": "OPTNETFEC",
"BSP_USE_NETWORK_SCC": "OPTNETSCC",
"BSP_USE_UART2": "OPTUART2",
"BSP_USE_UART_INTERRUPTS": "OPTUARTIRQ",
"BSP_VIDEO_80x50": "OPTVIDEO80X50",
"BSP_ZYNQMP_NOCACHE_LENGTH": "OPTNOCACHELEN",
"BSP_ZYNQMP_RAM_LENGTH": "OPTRAMLEN",
"BSP_ZYNQ_NOCACHE_LENGTH": "OPTNOCACHELEN",
"BSP_ZYNQ_RAM_LENGTH": "OPTRAMLEN",
"CD2401_INT_LEVEL": "OPTINTLVL",
"CD2401_IO_MODE": "OPTIOMODE",
"CD2401_USE_TERMIOS": "OPTUSETERM",
"CLOCK_DRIVER_USE_8254": "OPTCLK8253",
"CLOCK_DRIVER_USE_FAST_IDLE": "OPTCLKFASTIDLE",
"CLOCK_DRIVER_USE_ONLY_BOOT_PROCESSOR": "OPTCLKBOOTCPU",
"CLOCK_DRIVER_USE_TSC": "OPTCLKTSC",
"CONFIGURE_MALLOC_BSP_SUPPORTS_SBRK": "OPTSBRK",
"CONSOLE_BAUD": "OPTCONBAUD",
"CONSOLE_BAUDRATE": "OPTCONBAUD",
"CONSOLE_CHN": "OPTCONCHN",
"CONSOLE_MINOR": "OPTCONMINOR",
"CONSOLE_POLLED": "OPTCONPOLL",
"CONSOLE_USE_INTERRUPTS": "OPTCONIRQ",
"CONS_SCC1_MODE": "OPTCONSCC1",
"CONS_SCC2_MODE": "OPTCONSCC2",
"CONS_SCC3_MODE": "OPTCONSCC3",
"CONS_SCC4_MODE": "OPTCONSCC4",
"CONS_SMC1_MODE": "OPTCONSMC1",
"CONS_SMC2_MODE": "OPTCONSMC2",
"COPY_DATA_FROM_ROM": "OPTCPYDATA",
"CPU_CLOCK_RATE_HZ": "OPTCPUCLK",
"CPU_S3C2410": "OPTCPUS3C2410",
"csb637": "OPTCSB637",
"CYCLONE_V_CONFIG_CONSOLE": "OPTCONCFG",
"CYCLONE_V_CONFIG_UART_1": "OPTCONUART1",
"CYCLONE_V_I2C0_SPEED": "OPTI2CSPEED",
"CYCLONE_V_NO_I2C": "OPTNOI2C",
"CYCLONE_V_UART_BAUD": "OPTUARTBAUD",
"DISPATCH_HANDLER_STAT": "OPTDISPHANDSTAT",
"ENABLE_LCD": "OPTENLCD",
"ENABLE_UMON_CONSOLE": "OPTENUMONCON",
"ENABLE_UMON": "OPTENUMON",
"ENABLE_USART0": "OPTENUSART0",
"ENABLE_USART1": "OPTENUSART1",
"ENABLE_USART2": "OPTENUSART2",
"ENABLE_USART3": "OPTENUSART3",
"GEN68360_040": "OPT68360X040",
"GEN68360": "OPT68360",
"GEN83XX_ENABLE_INTERRUPT_NESTING": "OPTIRQNEST",
"HAS_DBUG": "OPTDBUG",
"HAS_LOW_LEVEL_INIT": "OPTLOWINIT",
"HAS_SMC91111": "OPTSMC91111",
"HAS_UBOOT": "OPTUBOOT",
"I2C_IO_MODE": "OPTI2CIOMODE",
"IDE_USE_PRIMARY_INTERFACE": "OPTIDEPRIIFC",
"IDE_USE_SECONDARY_INTERFACE": "OPTIDESECIFC",
"IMX_CCM_AHB_HZ": "OPTCCMAHB",
"IMX_CCM_IPG_HZ": "OPTCMMIPG",
"IMX_CCM_SDHCI_HZ": "OPTCMMSDHCI",
"IMX_CCM_UART_HZ": "OPTCMMUART",
"INTERRUPT_USE_TABLE": "OPTIRQTBL",
"IS_AM335X": "OPTAM335X",
"IS_DM3730": "OPTDM3730",
"LM32_ON_SIMULATOR": "OPTSIM",
"LM3S69XX_ENABLE_UART_0": "OPTENUART0",
"LM3S69XX_ENABLE_UART_1": "OPTENUART1",
"LM3S69XX_ENABLE_UART_2": "OPTENUART2",
"LM3S69XX_HAS_UDMA": "OPTUDMA",
"LM3S69XX_MCU_LM3S3749": "OPTLM3S3749",
"LM3S69XX_MCU_LM3S6965": "OPTLM3S6965",
"LM3S69XX_MCU_LM4F120": "OPTLM4F120",
"LM3S69XX_NUM_GPIO_BLOCKS": "OPTGPIONUM",
"LM3S69XX_NUM_SSI_BLOCKS": "OPTSSIBLKS",
"LM3S69XX_SSI_CLOCK": "OPTSSICLK",
"LM3S69XX_SYSTEM_CLOCK": "OPTSYSCLK",
"LM3S69XX_UART_BAUD": "OPTUARTBAUD",
"LM3S69XX_USE_AHB_FOR_GPIO": "OPTGPIOAHB",
"LM3S69XX_XTAL_CONFIG": "OPTXTALCFG",
"LPC176X_CCLK": "OPTCCLK",
"LPC176X_CONFIG_CONSOLE": "OPTCONCFG",
"LPC176X_CONFIG_UART_1": "OPTUART1CFG",
"LPC176X_OSCILLATOR_MAIN": "OPTOSCMAIN",
"LPC176X_OSCILLATOR_RTC": "OPTOSCRTC",
"LPC176X_PCLKDIV": "OPTPCLKDIV",
"LPC176X_STOP_GPDMA": "OPTSTOPGPDMA",
"LPC176X_STOP_USB": "OPTSTOPUSB",
"LPC176X_UART_BAUD": "OPTUARTBAUD",
"LPC24XX_CCLK": "OPTCCLK",
"LPC24XX_CONFIG_CONSOLE": "OPTCONCFG",
"LPC24XX_CONFIG_UART_1": "OPTUART1CFG",
"LPC24XX_CONFIG_UART_2": "OPTUART2CFG",
"LPC24XX_CONFIG_UART_3": "OPTUART3CFG",
"LPC24XX_EMCCLKDIV": "OPTEMCCLKDIV",
"LPC24XX_EMC_IS42S32800B":  "OPTEMCIS42S32800B",
"LPC24XX_EMC_IS42S32800D7": "OPTEMCIS42S32800D7",
"LPC24XX_EMC_M29W160E":     "OPTEMCM29W160E",
"LPC24XX_EMC_M29W320E70":   "OPTEMCM29W320E70",
"LPC24XX_EMC_MT48LC4M16A2": "OPTEMCMT48LC4M16A2",
"LPC24XX_EMC_SST39VF3201":  "OPTEMCSST39VF3201",
"LPC24XX_EMC_TEST":         "OPTEMCTEST",
"LPC24XX_EMC_W9825G2JB75I": "OPTEMCW9825G2JB75I",
"LPC24XX_ETHERNET_RMII": "OPTETHRMII",
"LPC24XX_HEAP_EXTEND": "OPTHEAPEXT",
"LPC24XX_OSCILLATOR_MAIN": "OPTOSCMAIN",
"LPC24XX_OSCILLATOR_RTC": "OPTOSCRTC",
"LPC24XX_PCLKDIV": "OPTPCLKDIV",
"LPC24XX_PIN_ETHERNET_POWER_DOWN": "OPTETHDOWNPIN",
"LPC24XX_STOP_ETHERNET": "OPTSTOPETH",
"LPC24XX_STOP_GPDMA": "OPTSTOPGPDMA",
"LPC24XX_STOP_USB": "OPTSTOPUSB",
"LPC24XX_UART_BAUD": "OPTUARTBAUD",
"LPC32XX_CONFIG_U3CLK": "OPTU3CLK",
"LPC32XX_CONFIG_U4CLK": "OPTU4CLK",
"LPC32XX_CONFIG_U5CLK": "OPTU5CLK",
"LPC32XX_CONFIG_U6CLK": "OPTU6CLK",
"LPC32XX_DISABLE_MMU": "OPTDISMMU",
"LPC32XX_DISABLE_READ_ONLY_PROTECTION": "OPTDISROPROT",
"LPC32XX_DISABLE_READ_WRITE_DATA_CACHE": "OPTDISRWDC",
"LPC32XX_ENABLE_WATCHDOG_RESET": "OPTENWDGRST",
"LPC32XX_ETHERNET_RMII": "OPTETHRMII",
"LPC32XX_OSCILLATOR_MAIN": "OPTOSCMAIN",
"LPC32XX_OSCILLATOR_RTC": "OPTOSCRTC",
"LPC32XX_PERIPH_CLK": "OPTPERIPHCLK",
"LPC32XX_SCRATCH_AREA_SIZE": "OPTSCRATCHSZ",
"LPC32XX_STOP_ETHERNET": "OPTSTOPETH",
"LPC32XX_STOP_GPDMA": "OPTSTOPGPDMA",
"LPC32XX_STOP_USB": "OPTSTOPUSB",
"LPC32XX_UART_1_BAUD": "OPTUART1BAUD",
"LPC32XX_UART_2_BAUD": "OPTUART2BAUD",
"LPC32XX_UART_3_BAUD": "OPTUART3BAUD",
"LPC32XX_UART_4_BAUD": "OPTUART4BAUD",
"LPC32XX_UART_5_BAUD": "OPTUART5BAUD",
"LPC32XX_UART_6_BAUD": "OPTUART6BAUD",
"LPC32XX_UART_7_BAUD": "OPTUART7BAUD",
"LPC_DMA_CHANNEL_COUNT": "OPTDMACHN",
"M5484FIREENGINE": "OPTM5484FIREENGINE",
"MPC5200_BOARD_BRS5L": "OPTBRS5L",
"MPC5200_BOARD_BRS6L": "OPTBRS6L",
"MPC5200_BOARD_DP2": "OPTDP2",
"MPC5200_BOARD_ICECUBE": "OPTICECUB",
"MPC5200_BOARD_PM520_CR825": "OPTPM520CR825",
"MPC5200_BOARD_PM520_ZE30": "OPTPM520ZE30",
"MPC5200_PSC_INDEX_FOR_GPS_MODULE": "OPTPSCGPS",
"MPC55XX_BOARD_GWLCFM": "OPTGWLCFM",
"MPC55XX_BOARD_MPC5566EVB": "OPTMPC5566EVB",
"MPC55XX_BOARD_MPC5674F_ECU508": "OPTMPC5674FECU508",
"MPC55XX_BOARD_MPC5674FEVB": "OPTMPC5674FEVB",
"MPC55XX_BOARD_MPC5674F_RSM6": "OPTMPC5674FRSM6",
"MPC55XX_BOARD_PHYCORE_MPC5554": "OPTPHYCOREMPC5554",
"MPC55XX_BOOTFLAGS": "OPTBOOTFLG",
"MPC55XX_CHIP_FAMILY": "OPTCHIPFAM",
"MPC55XX_CHIP_TYPE": "OPTCHIPTYPE",
"MPC55XX_CLOCK_EMIOS_CHANNEL": "OPTCLKEMIOS",
"MPC55XX_CLOCK_PIT_CHANNEL": "OPTCLKPIT",
"MPC55XX_CONSOLE_MINOR": "OPTCONMINOR",
"MPC55XX_EARLY_STACK_SIZE": "OPTEARLYSTKSZ",
"MPC55XX_EMIOS_PRESCALER": "OPTEMIOSPRESCAL",
"MPC55XX_ENABLE_START_PROLOGUE": "OPTENSTARTPRO",
"MPC55XX_ESCI_USE_INTERRUPTS": "OPTESCIIRQ",
"MPC55XX_FMPLL_ESYNCR1_CLKCFG": "OPTFMPLLESYNCR1",
"MPC55XX_FMPLL_MFD": "OFMPLLPTMFD",
"MPC55XX_FMPLL_PREDIV": "OPTFMPLLPREDIV",
"MPC55XX_NEEDS_LOW_LEVEL_INIT": "OPTLOWINIT",
"MPC55XX_NULL_POINTER_PROTECTION": "OPTNULLPROT",
"MPC55XX_REFERENCE_CLOCK": "OPTREFCLK",
"MPC55XX_SYSTEM_CLOCK_DIVIDER": "OPTSYSCLKDIV",
"MPC55XX_SYSTEM_CLOCK": "OPTSYSCLK",
"mpc603e": "OPTMPC603E",
"mpc750": "OPTMPC750",
"mpc8240": "OPTMPC8240",
"MPC83XX_BOARD_BR_UID": "OPTBRUID",
"MPC83XX_BOARD_HSC_CM01": "OPTHSCCM01",
"MPC83XX_BOARD_MPC8309SOM": "OPTMPC8309SOM",
"MPC83XX_BOARD_MPC8313ERDB": "OPTMPC8313ERDB",
"MPC83XX_BOARD_MPC8349EAMDS": "OPTMPC8349EAMDS",
"MPC83XX_CHIP_TYPE": "OPTCHIPTYPE",
"MPC83XX_HAS_NAND_LP_FLASH_ON_CS0": "OPTNANDCS0",
"MPC83XX_NETWORK_INTERFACE_0_PHY_ADDR": "OPTNET0PHY",
"mvme2100": "OPTMVME2100",
"NUM_APP_DRV_GDT_DESCRIPTORS": "OPTGDTDESC",
"ON_SKYEYE": "OPTSKYEYE",
"PGH360": "OPTPGH360",
"PPC_CACHE_ALIGNMENT": "OPTCACHEALIGN",
"PPC_CACHE_DATA_L1_SIZE": "OPTCACHEDATAL1SZ",
"PPC_CACHE_DATA_L2_SIZE": "OPTCACHEDATAL2SZ",
"PPC_CACHE_INSTRUCTION_L1_SIZE": "OPTCACHEINSTL1SZ",
"PPC_CACHE_INSTRUCTION_L2_SIZE": "OPTCACHEINSTL2SZ",
"PPC_EXC_CONFIG_BOOKE_ONLY": "OPTEXCBOOKE",
"PPC_EXC_CONFIG_USE_FIXED_HANDLER": "OPTEXCFIXDHDLR",
"__ppc_generic": "OPTPPCGENERIC",
"PPC_USE_DATA_CACHE": "OPTPPCCACHEDATA",
"PPC_USE_SPRG": "OPTSPRG",
"PPC_VECTOR_FILE_BASE": "OPTVECBASE",
"PRINTK_CHN": "OPTPRINTKCHN",
"PRINTK_MINOR": "OPTPRINTKMINOR",
"qemu": "OPTQEMU",
"QORIQ_BUS_CLOCK_DIVIDER": "OPTBUSCLKDIV",
"QORIQ_CHIP_NUMBER": "OPTCHIPNUM",
"QORIQ_CHIP_SERIES": "OPTCHIPSER",
"QORIQ_CLOCK_TIMECOUNTER": "OPTCLKTMCTR",
"QORIQ_CLOCK_TIMER": "OPTCLKTMR",
"QORIQ_CPU_COUNT": "OPTCPUCNT",
"QORIQ_ETSEC_1_PHY_ADDR": "OPTETSEC1PHY",
"QORIQ_ETSEC_2_PHY_ADDR": "OPTETSEC2PHY",
"QORIQ_ETSEC_3_PHY_ADDR": "OPTETSEC3PHY",
"QORIQ_HAS_HYPERVISOR_MODE": "OPTHYP",
"QORIQ_INITIAL_BUCSR": "OPTBUCSR",
"QORIQ_INITIAL_HID0": "OPTHID0",
"QORIQ_INITIAL_MSR": "OPTMSR",
"QORIQ_INITIAL_SPEFSCR": "OPTSPEFSCR",
"QORIQ_INTERCOM_AREA_BEGIN": "OPTICOMBEGIN",
"QORIQ_INTERCOM_AREA_SIZE": "OPTICOMSZ",
"QORIQ_IS_HYPERVISOR_GUEST": "OPTHYPGUEST",
"QORIQ_MMU_DEVICE_MAS7": "OPTMAS7",
"QORIQ_PHYSICAL_THREAD_COUNT": "OPTTHRDCNT",
"QORIQ_TLB1_ENTRY_COUNT": "OPTTLB1CNT",
"QORIQ_UART_0_ENABLE": "OPTUART0EN",
"QORIQ_UART_1_ENABLE": "OPTUART1EN",
"QORIQ_UART_BRIDGE_0_ENABLE": "OPTUARTBRG0EN",
"QORIQ_UART_BRIDGE_1_ENABLE": "OPTUARTBRG1EN",
"QORIQ_UART_BRIDGE_MASTER_CORE": "OPTUARTBRGMAS",
"QORIQ_UART_BRIDGE_SLAVE_CORE": "OPTUARTBRGSLV",
"QORIQ_UART_BRIDGE_TASK_PRIORITY": "OPTUARTBRGPRI",
"RISCV_CONSOLE_MAX_NS16550_DEVICES": "OPTNS16550MAX",
"RISCV_ENABLE_FRDME310ARTY_SUPPORT": "OPTFRDME310ARTY",
"RISCV_ENABLE_HTIF_SUPPORT": "OPTHTIF",
"RISCV_MAXIMUM_EXTERNAL_INTERRUPTS": "OPTEXTIRQMAX",
"RTEMS_BSP_I2C_EEPROM_DEVICE_NAME": "OPTEEPROMNAME",
"RTEMS_BSP_I2C_EEPROM_DEVICE_PATH": "OPTEEPROMPATH",
"RTEMS_XPARAMETERS_H": "OPTXPARAM",
"SIMSPARC_FAST_IDLE": "OPTCLKFASTIDLE",
"SINGLE_CHAR_MODE": "OPTSINGLECHAR",
"SMC91111_ENADDR_IS_SETUP": "OPTSMC9111ENADDR",
"SMSC9218I_BIG_ENDIAN_SUPPORT": "OPTSMC9218IBIGE",
"SMSC9218I_EDMA_RX_CHANNEL": "OPTSMC9218IRXCHN",
"SMSC9218I_EDMA_TX_CHANNEL": "OPTSMC9218ITXCHN",
"SMSC9218I_ENABLE_LED_OUTPUTS": "OPTSMC9218ILED",
"SMSC9218I_IRQ_PIN": "OPTSMC9218IPINIRQ",
"SMSC9218I_RESET_PIN": "OPTSMC9218IPINRST",
"SPI_IO_MODE": "OPTSPIIOMODE",
"STANDALONE_EVB": "OPTEVB",
"START_HW_INIT": "OPTLOWINIT",
"STM32F4_ENABLE_I2C1": "OPTENI2C1",
"STM32F4_ENABLE_I2C2": "OPTENI2C2",
"STM32F4_ENABLE_UART_4": "OPTENUART4",
"STM32F4_ENABLE_UART_5": "OPTENUART5",
"STM32F4_ENABLE_USART_1": "OPTENUSART1",
"STM32F4_ENABLE_USART_2": "OPTENUSART2",
"STM32F4_ENABLE_USART_3": "OPTENUSART3",
"STM32F4_ENABLE_USART_6": "OPTENUSART6",
"STM32F4_FAMILY_F10XXX": "OPTF10XXX",
"STM32F4_FAMILY_F4XXXX": "OPTF4XXXX",
"STM32F4_HCLK": "OPTHCLK",
"STM32F4_HSE_OSCILLATOR": "OPTOSCHSE",
"STM32F4_PCLK1": "OPTPCLK1",
"STM32F4_PCLK2": "OPTPCLK2",
"STM32F4_SYSCLK": "OPTSYSCLK",
"STM32F4_USART_BAUD": "OPTUSARTBAUD",
"TMS570_CCLK": "OPTCCLK",
"TMS570_OSCILLATOR_MAIN": "OPTOSCMAIN",
"TMS570_OSCILLATOR_RTC": "OPTOSCRTC",
"TMS570_SCI_BAUD_RATE": "OPTSCIBAUD",
"TMS570_USE_HWINIT_STARTUP": "OPTLOWINIT",
"UARTS_IO_MODE": "OPTUARTSIOMODE",
"UARTS_USE_TERMIOS_INT": "OPTUARTSTERMIRQ",
"UARTS_USE_TERMIOS": "OPTUARTSTERM",
"UART_USE_DMA": "OPTUARTDMA",
"USE_CIRRUS_GD5446": "OPTCIRRUS",
"USE_COM1_AS_CONSOLE": "OPTCONCOM1",
"USE_VBE_RM": "OPTVBERM",
"USE_VGA": "OPTVGA",
"VIRTEX_CONSOLE_USE_INTERRUPTS": "OPTCONIRQ",
"WATCHDOG_TIMEOUT": "OPTWDGTIMEOUT",
"ZYNQ_CLOCK_CPU_1X": "OPTCLKCPU1X",
"ZYNQ_CLOCK_UART": "OPTCLKUART",
"ZYNQ_CONSOLE_USE_INTERRUPTS": "OPTCONIRQ",
}

def make_list(name, lst, extra):
    if not lst:
        return f"""{name}: []"""
    lines = f"""{name}:"""
    for l in lst:
            lines += f"""
- {l}{extra}"""
    return lines

def make_uid(name):
    return name.upper().replace("_", "").replace("-", "")

class Family(object):
    def __init__(self, arch, name):
        self.arch = arch
        self.name = name
        self.short = make_uid(name)
        self.uid = f"RTEMS-BUILD-BSP-{make_uid(arch)}-{self.short}"
        self.bsps = {}
        self.options = {}
        self.install = {}
        self.source = []
        self.source_enabled_by = {}
        self.start = None
        self.linkcmds = "special"
        self.uids = set(["RTEMS-BUILD-BSP-BSPOPTS"])
        if name in families:
            raise Exception(name)
        families[name] = self

    def get_option(self, name):
        if name not in self.options:
            self.options[name] = Option(self, name)
        return self.options[name]

    def add_header(self, name, header):
        name = name.replace("_", "/").replace("include", "${BSP_INCLUDEDIR}")
        if name not in self.install:
            self.install[name] = []
        self.install[name].append(header)

    def add_data(self, data):
        name = "${BSP_LIBDIR}"
        if name not in self.install:
            self.install[name] = []
        self.install[name].append(data)

    def get_enabled_by(self, enable):
        enabled_by = []
        for e in enable:
            name = e[0]
            if name in enable_map:
                name = enable_map[name]
            elif name in enable_is_option:
                self.options[enable_is_option[name]].is_enable = True
            else:
                continue
            if e[1]:
                name = "not: " + name
            name.replace("not: not:", "not:")
            enabled_by.append(name)
        if not enabled_by:
                return None
        if len(enabled_by) == 1:
                return f"""enabled-by:
- {enabled_by[0]}"""
        r = """enabled-by:
- and:"""
        for e in enabled_by:
            r += f"""
  - {e}"""
        return r

    def add_source(self, name, enable):
        e = self.get_enabled_by(enable)
        if e is None:
            self.source.append(name)
            return
        if e not in self.source_enabled_by:
            self.source_enabled_by[e] = []
        self.source_enabled_by[e].append(name)

    def add_make_include(self, name):
        self.uids.add(make_include_to_uid[name])

    def set_start_file(self, name):
        if self.start is not None:
            raise Exception(self.name)
        self.start = name

    def get_install(self):
        if len(self.install) == 0:
            return "install: []"
        i = "install:"
        for k, v in sorted(self.install.items()):
            i += f"""
- destination: {k}
  source:"""
            for h in sorted(v):
                i += f"""
  - {h}"""
        return i

    def write_abi(self, specdir):
        abis = {}
        for b in sorted(self.bsps.values()):
            n = str(b.abi_flags)
            if n not in abis:
                abis[n] = (1, b.name, b.abi_flags, [b.name])
            else:
                a = abis[n]
                abis[n] = (a[0] + 1, a[1], a[2], a[3] + [b.name])
        first = True
        second = False
        d = "default:"
        for a in sorted(abis.values(), reverse=True):
            if first:
                first = False
                if a[2]:
                    for i in a[2]:
                        d += f"""
- {i}"""
                else:
                    d += " []"
                d += """
default-by-variant:"""
            else:
                second = True
                d += """
- value:"""
                if a[2]:
                    for i in a[2]:
                        d += f"""
  - {i}"""
                else:
                    d += " []"
                d += """
  variants:"""
                for i in sorted(a[3]):
                    d += f"""
  - {self.arch}/{i}"""
        if not second:
            d += " []"
        uid = f"{self.uid}-ABI"
        self.uids.add(uid)
        with open(specdir + "/" + uid + ".yml", "w") as f:
            f.write(f"""actions:
- get-string: null
- split: null
- env-append: null
active: true
build-type: option
{d}
derived: false
enabled-by: []
header: ''
level: 1.8
links: []
name: ABI_FLAGS
normative: true
order: 0
ref: ''
reviewed: null
text: |
  ABI flags
type: build
""")

    def write_linkcmds(self, specdir):
        if self.linkcmds == "normal":
            self.add_data(f"bsps/{self.arch}/{self.name}/start/linkcmds")
        elif self.linkcmds == "base":
            self.uids.add("RTEMS-BUILD-BSP-LINKCMDS")
        elif self.linkcmds == "shared":
            self.add_data(f"bsps/{self.arch}/shared/start/linkcmds")
        elif self.linkcmds == "special":
            self.uids.add(f"{self.uid}-LINKCMDS")
        else:
            raise Exception(self.name)

    def write_start_file(self, specdir):
        if self.start is None:
            return
        uid = f"{self.uid}-START"
        path = specdir + "/" + uid + ".yml"
        if self.start.endswith("/shared/start/start.S"):
            uid = f"RTEMS-BUILD-BSP-{make_uid(self.arch)}-START"
            path = specdir + "/../" + uid + ".yml"
        self.uids.add(uid)
        dest = "install-path: ${BSP_LIBDIR}"
        with open(path, "w") as f:
            f.write(f"""active: true
asflags: []
build-type: start-file
cppflags: []
derived: true
{dest}
enabled-by: []
header: ''
includes: []
level: 1.0
links: []
normative: true
order: 0
ref: ''
reviewed: NULL
source:
- {self.start}
target: start.o
text: ''
type: build
""")

    def write_source_enabled_by(self, specdir, k, v):
        uid = f"{self.uid}-OBJ{enable_by_to_obj[k]}"
        self.uids.add(uid)
        with open(specdir + "/" + uid + ".yml", "w") as f:
            f.write(f"""active: true
build-type: objects
cflags: []
cppflags: []
cxxflags: []
derived: false
{k}
header: ''
includes: []
install: []
level: 1.0
links: []
normative: true
order: 0
ref: ''
reviewed: null
{make_list("source", sorted(v), "")}
text: ''
type: build
""")

    def write_single_bsp(self, specdir):
        bsp = list(self.bsps.values())[0]
        uid = f"{self.uid}-BSP{self.short}"
        self.uids.add(bsp.get_optimize_uid())
        for u in bsp.uids:
            self.uids.add(u)
        with open(specdir + "/" + uid + ".yml", "w") as f:
            f.write(f"""active: true
arch: {self.arch}
bsp: {bsp.name}
build-type: bsp
cflags: []
cppflags: []
derived: true
enabled-by: []
family: {self.name}
header: ''
includes: []
{self.get_install()}
level: 1.0
{make_list("links", sorted(self.uids), ": null")}
normative: true
order: 0
ref: ''
reviewed: null
{make_list("source", sorted(self.source), "")}
text: ''
type: build
""")

    def write_objects(self, specdir):
        bsp = list(self.bsps.values())[0].name
        uid = f"{self.uid}-OBJ"
        self.uids.add(uid)
        with open(specdir + "/" + uid + ".yml", "w") as f:
            f.write(f"""active: true
build-type: objects
cflags: []
cppflags: []
cxxflags: []
derived: false
enabled-by: []
header: ''
includes: []
{self.get_install()}
level: 1.1
links: []
normative: true
order: 0
ref: ''
reviewed: null
{make_list("source", sorted(self.source), "")}
text: ''
type: build
""")

    def write_group(self, specdir):
        bsp = list(self.bsps.values())[0].name
        uid = f"{self.uid}-GRP"
        with open(specdir + "/" + uid + ".yml", "w") as f:
            f.write(f"""active: true
build-type: group
install: []
derived: true
enabled-by: []
header: ''
includes: []
ldflags: []
level: 1.22
{make_list("links", sorted(self.uids), ": null")}
normative: true
order: 0
ref: ''
reviewed: null
text: ''
top-level: false
type: build
use-before: []
use-after: []
""")

class BSP(object):
    def __init__(self, family, name):
        self.family = family
        self.name = name
        self.short = make_uid(name)
        if "QEMU" in self.short:
            self.short = "QEMU"
        elif self.short != family.short:
            maybe = self.short.replace(family.short, "")
            if len(maybe) > 3:
                self.short = maybe
        self.short = self.short
        self.is_enable = False
        self.tcfg_includes = set()
        self.tcfg_excludes = set()
        self.abi_flags = []
        self.uids = set()
        self.optimize = "O2"
        if name in family.bsps:
            raise Exception(name)
        family.bsps[name] = self

    def __lt__(self, other):
        return self.name <= other.name

    def add_tcfg_include(self, name):
        self.tcfg_includes.add(tcfg_include_to_uid[name])

    def add_tcfg_exclude(self, name):
        self.tcfg_excludes.add(name)

    def add_abi_flags(self, name):
        self.abi_flags.extend(name.split())

    def get_optimize_uid(self):
        return f"RTEMS-BUILD-BSP-OPT{self.optimize}"

    def write_tcfg(self, specdir):
        if self.tcfg_excludes:
            uid = f"{self.family.uid}-TST{self.short}"
            self.uids.add(uid)
            actions = "- set-test-state:"
            for e in sorted(self.tcfg_excludes):
                actions += f"""
    {e}: exclude"""
            with open(specdir + "/" + uid + ".yml", "w") as f:
                f.write(f"""actions:
{actions}
active: true
build-type: option
default: null
default-by-variant: []
derived: false
enabled-by: []
header: ''
level: 1.8
{make_list("links", sorted(self.tcfg_includes), ": null")}
normative: true
order: 0
ref: ''
reviewed: null
text: ''
type: build
""")
        else:
            for i in self.tcfg_includes:
                self.uids.add(i)

    def write_bsp(self, specdir):
        uid = f"{self.family.uid}-BSP{self.short}"
        self.uids.add(f"{self.family.uid}-GRP")
        self.uids.add(bsp.get_optimize_uid())
        with open(specdir + "/" + uid + ".yml", "w") as f:
            f.write(f"""active: true
arch: {self.family.arch}
bsp: {self.name}
build-type: bsp
cflags: []
cppflags: []
derived: true
enabled-by: []
family: {self.family.name}
header: ''
includes: []
install: []
level: 1.0
{make_list("links", sorted(self.uids), ": null")}
normative: true
order: 0
ref: ''
reviewed: null
source: []
text: ''
type: build
""")

class Option(object):
    def __init__(self, family, name):
        self.family = family
        self.name = name
        self.help = None
        self.values = {}
        self.is_enable = False
        self.format = "'{}'"
        family.options[name] = self

    def set_help(self, h):
        if self.help is not None:
            raise Exception(self.name)
        self.help = h

    def add_value(self, k, v):
        if k in self.values:
            raise Exception(self.name)
        self.values[k] = v

    def get_value(self, k, t):
        d = "false"
        if t == "int":
            d = "0";
        v = self.values.get(k, d)
        if t == "bool":
            if v == "" or v == "0":
                v = "false"
            elif v == "1":
                v = "true"
        return v

    def get_default_by_variant(self, t):
        if len(self.values) == 1:
            return "default-by-variant: []"
        d = "default-by-variant:"
        for k, v in self.values.items():
            if k == "*":
                continue
            kk = k.replace("*", ".*")
            d += f"""
- value: {self.get_value(k, t)}
  variants:
  - {self.family.arch}/{kk}"""
        return d

    def get_actions(self, t):
        a = ""
        if t == "int":
            a += """- get-integer: null
- define: null"""
        elif t == "bool":
            a += """- get-boolean: null
- define-condition: null"""
        elif t == "char" or t == "unquoted":
            a += """- get-string: null
- define-unquoted: null"""
        elif t == "string":
            a += """- get-string: null
- define: null"""
        if self.is_enable:
            a += """
- env-enable: null"""
        if t == "char" or t == "int" or t == "string" or t == "unquoted":
            a += f"""
format: {self.format}"""
        return a

    def determine_type(self, k, v, t):
        if self.name == "CONSOLE_USE_INTERRUPTS" or self.name == "PRINTK_MINOR":
            return "int"
        if len(v) == 0:
            return t
        if (v == "0" or v == "1") and t == "bool":
            return t
        m = re.search(r"^\\'(.)\\'$", v)
        if m:
            self.values[k] = m.group(1)
            self.format = "\"'{}'\""
            return "char"
        m = re.search(r"^'\"(.*)\"'$", v)
        if m:
            self.values[k] = m.group(1)
            return "string"
        m = re.search(r"^\\<(.*)\\>$", v)
        if m:
            self.values[k] = "<" + m.group(1) + ">"
            return "unquoted"
        m = re.search(r"^[(a-zA-Z]", v)
        if m:
            return "unquoted"
        m = re.search(r"^([0-9x]+)[uUlL]+$", v)
        if m:
            v = m.group(1)
            self.values[k] = v
        m = re.search(r"^([0-9]+)M$", v)
        if m:
            v = str(int(m.group(1)) * 1024 * 1024)
            self.values[k] = v
            self.format = "'{:#010x}'"
        m = re.search(r"^([0-9]+)K$", v)
        if m:
            v = str(int(m.group(1)) * 1024)
            self.values[k] = v
            self.format = "'{:#010x}'"
        try:
            int(v, 0)
            if v.startswith("0x"):
                self.format = "'{:#010x}'"
            return "int"
        except:
            return t

    def get_type(self):
        t = "bool"
        if len(self.values) == 1:
            for k, v in self.values.items():
                return self.determine_type(k, v, t)
        for k, v in self.values.items():
            if k == "*":
                self.determine_type(k, v, t)
                continue
            t = self.determine_type(k, v, t)
        if "*" in self.values:
            return self.determine_type("*", v, t)
        return t

    def write(self, specdir):
        uid = self.family.uid + "-" + option_to_uid[self.name]
        self.family.uids.add(uid)
        t = self.get_type()
        try:
            default = self.values["*"]
        except:
            pass
        default = self.get_value("*", t)
        self.values["*"] = default
        with open(specdir + "/" + uid + ".yml", "w") as f:
            f.write(f"""actions:
{self.get_actions(t)}
active: true
build-type: option
default: {default}
{self.get_default_by_variant(t)}
derived: false
enabled-by: []
header: ''
level: 1.8
links: []
name: {self.name}
normative: true
order: 0
ref: ''
reviewed: null
text: |
  {self.help}
type: build
""")

def push_enable(family, enable, name, is_not):
    enable.append((name, is_not))

def visit_arch(arch):
    archdir = "c/src/lib/libbsp/" + arch
    for name in os.listdir(archdir):
        try:
            with open(archdir + "/" + name + "/configure.ac", "r") as f:
                fam = Family(arch, name)
                for line in f:
                    line = line.strip()
                    m = re.search(r"RTEMS_BSPOPTS_HELP\(\s*\[(\w+)\],\s*\[(.*)\]\)", line)
                    if m:
                        o = fam.get_option(m.group(1))
                        o.set_help(m.group(2))
                        continue
                    m = re.search(r"RTEMS_BSPOPTS_SET\(\s*\[(\w+)\],\s*\[(.*)\],\s*\[(.*)\]\)", line)
                    if m:
                        o = fam.get_option(m.group(1))
                        o.add_value(m.group(2), m.group(3))
                        continue
                    m = re.search(r"RTEMS_BSP_LINKCMDS", line)
                    if m:
                        if os.path.isfile(f"bsps/{arch}/{name}/start/linkcmds.{name}"):
                            fam.linkcmds = "family"
                        elif os.path.isfile(f"bsps/{arch}/{name}/start/linkcmds"):
                            fam.linkcmds = "normal"
                        else:
                            fam.linkcmds = "base"
                        continue
        except NotADirectoryError:
            continue
        except FileNotFoundError:
            continue

        with open(archdir + "/" + name + "/Makefile.am", "r") as f:
            lines = f.read().replace('\\\n', '').split('\n')
            enable = []
            for line in lines:
                line = line.strip()
                m = re.search(r"if\s+(\w+)", line)
                if m:
                    push_enable(fam, enable, m.group(1), False)
                    continue
                m = re.search(r"if\s+!(\w+)", line)
                if m:
                    push_enable(fam, enable, m.group(1), True)
                    continue
                m = re.search(r"else", line)
                if m:
                    e = enable.pop()
                    push_enable(fam, enable, e, True)
                    continue
                m = re.search(r"endif", line)
                if m:
                    enable.pop()
                    continue
                m = re.search(r"librtemsbsp_a_SOURCES\s*.=.*/(bsps/.*)", line)
                if m:
                    fam.add_source(m.group(1), enable)
                    continue
                m = re.search(r"librtemsbsp_a_SOURCES\s*.=\s*\w+", line)
                if m:
                    raise Exception(fam.name + ": " + line)
                m = re.search(r"include.*/(bsps/.*sources.am)", line)
                if m:
                    fam.add_make_include(m.group(1))
                    continue
                m = re.search(r"^\s*start\.\$\(OBJEXT\):.*/(bsps/.*)", line)
                if m:
                    fam.set_start_file(m.group(1))
                    continue
                m = re.search(r"project_lib_DATA\s*.=.*/(bsps/.*)", line)
                if m:
                    fam.add_data(m.group(1))
                    continue

        with open("bsps/" + arch + "/" + name + "/headers.am", "r") as f:
            lines = f.read().replace('\\\n', '').split('\n')
            for line in lines:
                line = line.strip()
                m = re.search(r"(\w+)_HEADERS\s*.=.*/(bsps/.*)", line)
                if m:
                    fam.add_header(m.group(1), m.group(2))
                    continue
                m = re.search(r"include_HEADERS\s*\+=\s*include/bspopts.h", line)
                if m:
                    continue
                m = re.search(r"(\w+)_HEADERS\s*.=.*\w+", line)
                if m:
                    raise Exception(fam.name + ": " + line)
                    continue

def create_doorstop_arch(arch):
    os.makedirs(f"spec/build/bsps/{arch}", exist_ok=True)
    with open("spec/build/bsps/" + arch + "/.doorstop.yml", "w") as f:
        f.write(f"""settings:
  digits: 3
  parent: RTEMS-BUILD-BSP
  prefix: RTEMS-BUILD-BSP-{make_uid(arch)}
  sep: '-'
attributes:
  defaults:
    build-type: objects
    enabled-by: []
    order: 0
    type: build
""")

def create_doorstop_family(arch, family):
    os.makedirs(f"spec/build/bsps/{arch}/{family}", exist_ok=True)
    with open(f"spec/build/bsps/{arch}/{family}/.doorstop.yml", "w") as f:
        f.write(f"""settings:
  digits: 3
  parent: RTEMS-BUILD-BSP-{make_uid(arch)}
  prefix: RTEMS-BUILD-BSP-{make_uid(arch)}-{make_uid(family)}
  sep: '-'
attributes:
  defaults:
    build-type: objects
    enabled-by: []
    order: 0
    type: build
""")

for arch in archs:
    visit_arch(arch)

def process_cfg_file(fam, bsp, base, name):
    if name == "default.cfg":
        return
    with open(base + name, "r") as f:
        lines = f.read().replace('\\\n', '').split('\n')
        for line in lines:
            line = line.strip()
            m = re.search(r"^\s*#", line)
            if m:
                continue
            m = re.search(r"include \s*[\S]+/([\w.-]+)", line)
            if m:
                process_cfg_file(fam, bsp, base, m.group(1))
                continue
            m = re.search(r"CPU_CFLAGS\s*.=\s*(.*)", line)
            if m:
                bsp.add_abi_flags(m.group(1))
                continue
            m = re.search(r"CFLAGS_OPTIMIZE_V.*[\s=]+-(O.)\s+", line)
            if m:
                bsp.optimize = m.group(1).upper()
                continue

for fam in families.values():
    bspcfgdir = "bsps/" + fam.arch + "/" + fam.name + "/config"
    for name in os.listdir(bspcfgdir):
        if name.endswith(".cfg"):
            bsp = BSP(fam, name.replace(".cfg", ""))

            process_cfg_file(fam, bsp, "bsps/" + fam.arch + "/" + fam.name + "/config/", name)

            try:
                with open("bsps/" + fam.arch + "/" + fam.name + "/config/" + bsp.name + "-testsuite.tcfg", "r") as f:
                    lines = f.read().replace('\\\n', '').split('\n')
                    for line in lines:
                        line = line.strip()
                        m = re.search(r"include:\s*([\S]+)", line)
                        if m:
                            bsp.add_tcfg_include(m.group(1))
                            continue
                        m = re.search(r"exclude:\s*(\w+)", line)
                        if m:
                            bsp.add_tcfg_exclude(m.group(1))
                            continue
                        m = re.search(r"\w+:\s*\w+", line)
                        if m:
                            raise Exception(bsp.name + ": " + line)
                            continue
            except FileNotFoundError:
                pass

            if bsp.name != fam.name and fam.linkcmds == "family":
                if os.path.isfile(f"bsps/{fam.arch}/{fam.name}/start/linkcmds.{bsp.name}"):
                    fam.linkcmds = "base"
    if fam.linkcmds == "special" and os.path.isfile(f"bsps/{fam.arch}/shared/start/linkcmds"):
        fam.linkcmds = "shared"

def print_info():
    for fam in families.values():
        specdir = "spec/build/bsps/" + fam.arch + "/" + fam.name
        os.makedirs(specdir, exist_ok=True)
        print(f"{fam.arch}\n\t{fam.name}")
        print("\t\tbsps")
        for b in fam.bsps.values():
            print(f"\t\t\t{b.name}")
            if b.tcfg_includes:
                print("\t\t\t\ttcfg includes")
                for i in b.tcfg_includes:
                    print(f"\t\t\t\t\t{i}")
            if b.tcfg_excludes:
                print("\t\t\t\ttcfg excludes")
                for e in b.tcfg_excludes:
                    print(f"\t\t\t\t\t{e}")
            print("\t\t\t\tabi flags")
            for a in b.abi_flags:
                print(f"\t\t\t\t\t{a}")
        print("\t\tstart")
        print(f"\t\t\t{fam.start}")
        print("\t\toptions")
        for o in fam.options.values():
            print(f"\t\t\t{o.name}")
            print(f"\t\t\t\t{o.help}")
            for k, v in o.values.items():
                print(f"\t\t\t\t{k}: {v}")
        print("\t\tinstall")
        for k, v in fam.install.items():
            print(f"\t\t\t{k}")
            for h in v:
                print(f"\t\t\t\t{h}")
        print("\t\tsource")
        for k, v in fam.source_enabled_by.items():
            print(f"\t\t\t{k}")
            for h in v:
                print(f"\t\t\t\t{h}")
        print(f"\t\tlinkcmds {fam.linkcmds}")

def gen_spec():
    for fam in families.values():
        create_doorstop_arch(fam.arch)
        create_doorstop_family(fam.arch, fam.name)
        specdir = "spec/build/bsps/" + fam.arch + "/" + fam.name
        fam.write_abi(specdir)
        for o in fam.options.values():
            o.write(specdir)
        for b in fam.bsps.values():
            b.write_tcfg(specdir)
        for k, v in fam.source_enabled_by.items():
            fam.write_source_enabled_by(specdir, k, v)
        fam.write_start_file(specdir)
        fam.write_linkcmds(specdir)
        if len(fam.bsps) == 1:
            fam.write_single_bsp(specdir)
        else:
            fam.write_objects(specdir)
            fam.write_group(specdir)
            for b in fam.bsps.values():
                b.write_bsp(specdir)

gen_spec()
