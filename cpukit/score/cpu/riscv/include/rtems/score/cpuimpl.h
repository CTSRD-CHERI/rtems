/**
 * @file
 *
 * @brief CPU Port Implementation API
 */

/*
 * Copyright (c) 2013, 2018 embedded brains GmbH
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */

#ifndef _RTEMS_SCORE_CPUIMPL_H
#define _RTEMS_SCORE_CPUIMPL_H

#include <rtems/score/cpu.h>

/**
 * @defgroup RTEMSScoreCPURISCV RISC-V
 *
 * @ingroup RTEMSScoreCPU
 *
 * @brief RISCV Architecture Support
 *
 * @{
 */

#if defined(__riscv_atomic) && __riscv_xlen == 64
#if defined(__CHERI__) && __riscv_clen == 128
#define CPU_PER_CPU_CONTROL_SIZE 80
#else
#define CPU_PER_CPU_CONTROL_SIZE 48
#endif
#elif defined(__riscv_atomic) && __riscv_xlen == 32
#if defined(__CHERI__) && __riscv_clen == 64
#define CPU_PER_CPU_CONTROL_SIZE 56
#else
#define CPU_PER_CPU_CONTROL_SIZE 32
#endif
#elif __riscv_xlen == 64
#if defined(__CHERI__) && __riscv_clen == 128
#define CPU_PER_CPU_CONTROL_SIZE 64
#else
#define CPU_PER_CPU_CONTROL_SIZE 32
#endif
#elif __riscv_xlen == 32
#if defined(__CHERI__) && __riscv_clen == 64
#define CPU_PER_CPU_CONTROL_SIZE 32
#else
#define CPU_PER_CPU_CONTROL_SIZE 16
#endif
#endif

#define ALIGN_UP(n, b) (((((n) - 1) >> (b)) + 1) << (b))

#ifdef RTEMS_SMP
#define RISCV_CONTEXT_IS_EXECUTING 0
#endif

#define RISCV_CONTEXT_ISR_DISPATCH_DISABLE (1 * RISCV_GPR_SIZE)

/* The offset, in bytes, of the very first GPR in the Context_Control struct */
#define RISCV_CONTEXT_REG_BASE (2 * RISCV_GPR_SIZE)

#define RISCV_CONTEXT_RA (RISCV_CONTEXT_REG_BASE + (0 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_SP (RISCV_CONTEXT_REG_BASE + (1 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_TP (RISCV_CONTEXT_REG_BASE + (2 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S0 (RISCV_CONTEXT_REG_BASE + (3 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S1 (RISCV_CONTEXT_REG_BASE + (4 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S2 (RISCV_CONTEXT_REG_BASE + (5 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S3 (RISCV_CONTEXT_REG_BASE + (6 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S4 (RISCV_CONTEXT_REG_BASE + (7 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S5 (RISCV_CONTEXT_REG_BASE + (8 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S6 (RISCV_CONTEXT_REG_BASE + (9 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S7 (RISCV_CONTEXT_REG_BASE + (10 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S8 (RISCV_CONTEXT_REG_BASE + (11 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S9 (RISCV_CONTEXT_REG_BASE + (12 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S10 (RISCV_CONTEXT_REG_BASE + (13 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_S11 (RISCV_CONTEXT_REG_BASE + (14 * RISCV_GPR_SIZE))

#define RISCV_CONTEXT_FCSR (RISCV_CONTEXT_REG_BASE + (15 * RISCV_GPR_SIZE))
#define RISCV_CONTEXT_F( x ) ( (RISCV_CONTEXT_FCSR + 8) + RISCV_FPR_SIZE * x )

/* There are two CSR registers before the GPRs */
#define RISCV_INTERRUPT_FRAME_GPR_BASE (2 * RISCV_CSR_SIZE)

#define RISCV_INTERRUPT_FRAME_MSTATUS (0 * RISCV_CSR_SIZE)
#define RISCV_INTERRUPT_FRAME_MEPC    (1 * RISCV_CSR_SIZE)

#define RISCV_INTERRUPT_FRAME_A2      (RISCV_INTERRUPT_FRAME_GPR_BASE + (0 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_S0      (RISCV_INTERRUPT_FRAME_GPR_BASE + (1 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_S1      (RISCV_INTERRUPT_FRAME_GPR_BASE + (2 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_RA      (RISCV_INTERRUPT_FRAME_GPR_BASE + (3 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_A3      (RISCV_INTERRUPT_FRAME_GPR_BASE + (4 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_A4      (RISCV_INTERRUPT_FRAME_GPR_BASE + (5 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_A5      (RISCV_INTERRUPT_FRAME_GPR_BASE + (6 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_A6      (RISCV_INTERRUPT_FRAME_GPR_BASE + (7 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_A7      (RISCV_INTERRUPT_FRAME_GPR_BASE + (8 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_T0      (RISCV_INTERRUPT_FRAME_GPR_BASE + (9 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_T1      (RISCV_INTERRUPT_FRAME_GPR_BASE + (10 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_T2      (RISCV_INTERRUPT_FRAME_GPR_BASE + (11 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_T3      (RISCV_INTERRUPT_FRAME_GPR_BASE + (12 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_T4      (RISCV_INTERRUPT_FRAME_GPR_BASE + (13 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_T5      (RISCV_INTERRUPT_FRAME_GPR_BASE + (14 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_T6      (RISCV_INTERRUPT_FRAME_GPR_BASE + (15 * RISCV_GPR_SIZE))

#ifndef __riscv_flen

#define RISCV_INTERRUPT_FRAME_A0     (RISCV_INTERRUPT_FRAME_GPR_BASE + (16 * RISCV_GPR_SIZE))
#define RISCV_INTERRUPT_FRAME_A1     (RISCV_INTERRUPT_FRAME_GPR_BASE + (17 * RISCV_GPR_SIZE))

#define CPU_INTERRUPT_FRAME_SIZE     (2 * RISCV_CSR_SIZE) + (18 * RISCV_GPR_SIZE)

#else /* __riscv_flen == 32 ||  __riscv_flen == 64 */

#define RISCV_INTERRUPT_FRAME_FCSR   (2 * RISCV_CSR_SIZE) + (16 * RISCV_GPR_SIZE)

#define RISCV_INTERRUPT_FRAME_F( x ) ( ALIGN_UP((RISCV_INTERRUPT_FRAME_FCSR + 4), RISCV_FPR_SIZE_BITS) + RISCV_FPR_SIZE * x )

#define RISCV_INTERRUPT_FRAME_A0     ALIGN_UP(RISCV_INTERRUPT_FRAME_F( 20 ), RISCV_GPR_SIZE_BITS)
#define RISCV_INTERRUPT_FRAME_A1     RISCV_INTERRUPT_FRAME_A0 + RISCV_GPR_SIZE

//#define CPU_INTERRUPT_FRAME_SIZE     (2 * RISCV_CSR_SIZE) + (18 * RISCV_GPR_SIZE) + 4 + (20 * RISCV_FPR_SIZE)
#define CPU_INTERRUPT_FRAME_SIZE     RISCV_INTERRUPT_FRAME_A1 + RISCV_GPR_SIZE
#endif /* __riscv_flen */

#define RISCV_EXCEPTION_FRAME_X( x ) ( CPU_INTERRUPT_FRAME_SIZE + RISCV_GPR_SIZE * x )


#define RISCV_EXCEPTION_FRAME_MCAUSE RISCV_EXCEPTION_FRAME_X( 0 )
#define RISCV_EXCEPTION_FRAME_SP RISCV_EXCEPTION_FRAME_X( 1 )
#define RISCV_EXCEPTION_FRAME_GP RISCV_EXCEPTION_FRAME_X( 2 )
#define RISCV_EXCEPTION_FRAME_TP RISCV_EXCEPTION_FRAME_X( 3 )
#define RISCV_EXCEPTION_FRAME_S2 RISCV_EXCEPTION_FRAME_X( 4 )
#define RISCV_EXCEPTION_FRAME_S3 RISCV_EXCEPTION_FRAME_X( 5 )
#define RISCV_EXCEPTION_FRAME_S4 RISCV_EXCEPTION_FRAME_X( 6 )
#define RISCV_EXCEPTION_FRAME_S5 RISCV_EXCEPTION_FRAME_X( 7 )
#define RISCV_EXCEPTION_FRAME_S6 RISCV_EXCEPTION_FRAME_X( 8 )
#define RISCV_EXCEPTION_FRAME_S7 RISCV_EXCEPTION_FRAME_X( 9 )
#define RISCV_EXCEPTION_FRAME_S8 RISCV_EXCEPTION_FRAME_X( 10 )
#define RISCV_EXCEPTION_FRAME_S9 RISCV_EXCEPTION_FRAME_X( 11 )
#define RISCV_EXCEPTION_FRAME_S10 RISCV_EXCEPTION_FRAME_X( 12 )
#define RISCV_EXCEPTION_FRAME_S11 RISCV_EXCEPTION_FRAME_X( 13 )

#if __riscv_flen > 0

#define RISCV_CONTEXT_FS0 RISCV_CONTEXT_F( 0 )
#define RISCV_CONTEXT_FS1 RISCV_CONTEXT_F( 1 )
#define RISCV_CONTEXT_FS2 RISCV_CONTEXT_F( 2 )
#define RISCV_CONTEXT_FS3 RISCV_CONTEXT_F( 3 )
#define RISCV_CONTEXT_FS4 RISCV_CONTEXT_F( 4 )
#define RISCV_CONTEXT_FS5 RISCV_CONTEXT_F( 5 )
#define RISCV_CONTEXT_FS6 RISCV_CONTEXT_F( 6 )
#define RISCV_CONTEXT_FS7 RISCV_CONTEXT_F( 7 )
#define RISCV_CONTEXT_FS8 RISCV_CONTEXT_F( 8 )
#define RISCV_CONTEXT_FS9 RISCV_CONTEXT_F( 9 )
#define RISCV_CONTEXT_FS10 RISCV_CONTEXT_F( 10 )
#define RISCV_CONTEXT_FS11 RISCV_CONTEXT_F( 11 )

#define RISCV_INTERRUPT_FRAME_FT0 RISCV_INTERRUPT_FRAME_F( 0 )
#define RISCV_INTERRUPT_FRAME_FT1 RISCV_INTERRUPT_FRAME_F( 1 )
#define RISCV_INTERRUPT_FRAME_FT2 RISCV_INTERRUPT_FRAME_F( 2 )
#define RISCV_INTERRUPT_FRAME_FT3 RISCV_INTERRUPT_FRAME_F( 3 )
#define RISCV_INTERRUPT_FRAME_FT4 RISCV_INTERRUPT_FRAME_F( 4 )
#define RISCV_INTERRUPT_FRAME_FT5 RISCV_INTERRUPT_FRAME_F( 5 )
#define RISCV_INTERRUPT_FRAME_FT6 RISCV_INTERRUPT_FRAME_F( 6 )
#define RISCV_INTERRUPT_FRAME_FT7 RISCV_INTERRUPT_FRAME_F( 7 )
#define RISCV_INTERRUPT_FRAME_FT8 RISCV_INTERRUPT_FRAME_F( 8 )
#define RISCV_INTERRUPT_FRAME_FT9 RISCV_INTERRUPT_FRAME_F( 9 )
#define RISCV_INTERRUPT_FRAME_FT10 RISCV_INTERRUPT_FRAME_F( 10 )
#define RISCV_INTERRUPT_FRAME_FT11 RISCV_INTERRUPT_FRAME_F( 11 )
#define RISCV_INTERRUPT_FRAME_FA0 RISCV_INTERRUPT_FRAME_F( 12 )
#define RISCV_INTERRUPT_FRAME_FA1 RISCV_INTERRUPT_FRAME_F( 13 )
#define RISCV_INTERRUPT_FRAME_FA2 RISCV_INTERRUPT_FRAME_F( 14 )
#define RISCV_INTERRUPT_FRAME_FA3 RISCV_INTERRUPT_FRAME_F( 15 )
#define RISCV_INTERRUPT_FRAME_FA4 RISCV_INTERRUPT_FRAME_F( 16 )
#define RISCV_INTERRUPT_FRAME_FA5 RISCV_INTERRUPT_FRAME_F( 17 )
#define RISCV_INTERRUPT_FRAME_FA6 RISCV_INTERRUPT_FRAME_F( 18 )
#define RISCV_INTERRUPT_FRAME_FA7 RISCV_INTERRUPT_FRAME_F( 19 )

#define RISCV_EXCEPTION_FRAME_F( x ) ( RISCV_EXCEPTION_FRAME_X( 14 ) + RISCV_FPR_SIZE * x )

#define RISCV_EXCEPTION_FRAME_FS0 RISCV_EXCEPTION_FRAME_F( 0 )
#define RISCV_EXCEPTION_FRAME_FS1 RISCV_EXCEPTION_FRAME_F( 1 )
#define RISCV_EXCEPTION_FRAME_FS2 RISCV_EXCEPTION_FRAME_F( 2 )
#define RISCV_EXCEPTION_FRAME_FS3 RISCV_EXCEPTION_FRAME_F( 3 )
#define RISCV_EXCEPTION_FRAME_FS4 RISCV_EXCEPTION_FRAME_F( 4 )
#define RISCV_EXCEPTION_FRAME_FS5 RISCV_EXCEPTION_FRAME_F( 5 )
#define RISCV_EXCEPTION_FRAME_FS6 RISCV_EXCEPTION_FRAME_F( 6 )
#define RISCV_EXCEPTION_FRAME_FS7 RISCV_EXCEPTION_FRAME_F( 7 )
#define RISCV_EXCEPTION_FRAME_FS8 RISCV_EXCEPTION_FRAME_F( 8 )
#define RISCV_EXCEPTION_FRAME_FS9 RISCV_EXCEPTION_FRAME_F( 9 )
#define RISCV_EXCEPTION_FRAME_FS10 RISCV_EXCEPTION_FRAME_F( 10 )
#define RISCV_EXCEPTION_FRAME_FS11 RISCV_EXCEPTION_FRAME_F( 11 )

#define RISCV_EXCEPTION_CHERI_FRAME_MCCSR RISCV_EXCEPTION_FRAME_F( 12 )

#define RISCV_EXCEPTION_FRAME_C( x ) (RISCV_EXCEPTION_CHERI_FRAME_MCCSR + 16 + RISCV_GPR_SIZE * x)
#define RISCV_EXCEPTION_CHERI_FRAME_PCC       RISCV_EXCEPTION_FRAME_C( 0 )
#define RISCV_EXCEPTION_CHERI_FRAME_DDC       RISCV_EXCEPTION_FRAME_C( 1 )
#define RISCV_EXCEPTION_CHERI_FRAME_MTCC      RISCV_EXCEPTION_FRAME_C( 2 )
#define RISCV_EXCEPTION_CHERI_FRAME_MTDC      RISCV_EXCEPTION_FRAME_C( 3 )
#define RISCV_EXCEPTION_CHERI_FRAME_MSCRATCHC RISCV_EXCEPTION_FRAME_C( 4 )
#define RISCV_EXCEPTION_CHERI_FRAME_MEPCC     RISCV_EXCEPTION_FRAME_C( 5 )
#else

#define RISCV_EXCEPTION_CHERI_FRAME_MCCSR RISCV_EXCEPTION_FRAME_X ( 14 )

#define RISCV_EXCEPTION_FRAME_C( x ) (RISCV_EXCEPTION_CHERI_FRAME_MCCSR + 16 + RISCV_GPR_SIZE * x)
#define RISCV_EXCEPTION_CHERI_FRAME_PCC       RISCV_EXCEPTION_FRAME_C( 0 )
#define RISCV_EXCEPTION_CHERI_FRAME_DDC       RISCV_EXCEPTION_FRAME_C( 1 )
#define RISCV_EXCEPTION_CHERI_FRAME_MTCC      RISCV_EXCEPTION_FRAME_C( 2 )
#define RISCV_EXCEPTION_CHERI_FRAME_MTDC      RISCV_EXCEPTION_FRAME_C( 3 )
#define RISCV_EXCEPTION_CHERI_FRAME_MSCRATCHC RISCV_EXCEPTION_FRAME_C( 4 )
#define RISCV_EXCEPTION_CHERI_FRAME_MEPCC     RISCV_EXCEPTION_FRAME_C( 5 )

#endif /* __riscv_flen */

#ifndef ASM

#ifdef __cplusplus
extern "C" {
#endif

/* Core Local Interruptor (CLINT) */

typedef union {
  uint64_t val_64;
  uint32_t val_32[2];
} RISCV_CLINT_timer_reg;

typedef struct {
  uint32_t msip[4096];
  RISCV_CLINT_timer_reg mtimecmp[2048];
  uint32_t reserved_8000[4094];
  RISCV_CLINT_timer_reg mtime;
  uint32_t reserved_c000[4096];
} RISCV_CLINT_regs;

/* Platform-Level Interrupt Controller (PLIC) */

#define RISCV_PLIC_MAX_INTERRUPTS 1024

typedef struct {
  uint32_t priority_threshold;
  uint32_t claim_complete;
  uint32_t reserved_8[1022];
} RISCV_PLIC_hart_regs;

typedef struct {
  uint32_t priority[RISCV_PLIC_MAX_INTERRUPTS];
  uint32_t pending[1024];
  uint32_t enable[16320][32];
  RISCV_PLIC_hart_regs harts[CPU_MAXIMUM_PROCESSORS];
} RISCV_PLIC_regs;

typedef struct {
#ifdef __riscv_atomic
  uint64_t clear_reservations;
  uint32_t reserved_for_alignment_of_interrupt_frame[ 2 ];
#endif
  volatile RISCV_PLIC_hart_regs *plic_hart_regs;
  volatile uint32_t *plic_m_ie;
  volatile RISCV_CLINT_timer_reg *clint_mtimecmp;
  volatile uint32_t *clint_msip;
} CPU_Per_CPU_control;

struct Per_CPU_Control;

void _RISCV_Interrupt_dispatch(
  RISCV_CSR_Register      mcause,
  struct Per_CPU_Control *cpu_self
);

static inline uint32_t _RISCV_Read_FCSR( void )
{
  uint32_t fcsr;

  __asm__ volatile ( "frcsr %0" : "=&r" ( fcsr ) );

  return fcsr;
}

/*
 * The RISC-V ISA provides a rdtime instruction, however, it is implemented in
 * most chips via a trap-and-emulate.  Using this in machine mode makes no
 * sense.  Use the memory-mapped mtime register directly instead.  The address
 * of this register is platform-specific and provided via the device tree.
 *
 * To allow better code generation provide a const (_RISCV_Counter) and a
 * mutable (_RISCV_Counter_mutable) declaration for this pointer variable
 * (defined in assembler code).
 *
 * See code generated for this test case:
 *
 * extern volatile int * const c;
 *
 * extern volatile int *v;
 *
 * int fc(void)
 * {
 *   int a = *c;
 *   __asm__ volatile("" ::: "memory");
 *   return *c - a;
 * }
 *
 * int fv(void)
 * {
 *   int a = *v;
 *   __asm__ volatile("" ::: "memory");
 *   return *v - a;
 * }
 */
extern volatile uint32_t *_RISCV_Counter_mutable;

/*
 * Initial value of _RISCV_Counter and _RISCV_Counter_mutable.  Must be
 * provided by the BSP.
 */
extern volatile uint32_t _RISCV_Counter_register;

#ifdef RTEMS_SMP

static inline struct Per_CPU_Control *_RISCV_Get_current_per_CPU_control( void )
{
  struct Per_CPU_Control *cpu_self;

#if __CHERI__
  RISCV_CSR_Register cpu = (RISCV_CSR_Register) cpu_self;
  __asm__ volatile ( "csrr %0, mscratch" : "=r" ( cpu ) );

  return (Per_CPU_Control *) cpu;
#else
  __asm__ volatile ( "csrr %0, mscratch" : "=r" ( cpu_self ) );

  return cpu_self;
#endif /* __CHERI__ */

}

#define _CPU_Get_current_per_CPU_control() _RISCV_Get_current_per_CPU_control()

#endif /* RTEMS_SMP */

void _CPU_Context_volatile_clobber( uintptr_t pattern );

void _CPU_Context_validate( uintptr_t pattern );

RTEMS_INLINE_ROUTINE void _CPU_Instruction_illegal( void )
{
  __asm__ volatile ( "unimp" );
}

RTEMS_INLINE_ROUTINE void _CPU_Instruction_no_operation( void )
{
  __asm__ volatile ( "nop" );
}

#ifdef __cplusplus
}
#endif

#endif /* ASM */

/** @} */

#endif /* _RTEMS_SCORE_CPUIMPL_H */
