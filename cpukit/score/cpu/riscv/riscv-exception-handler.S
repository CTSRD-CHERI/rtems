/**
 * @file
 *
 * @addtogroup RTEMSScoreCPURISCV
 *
 * @brief RISC-V exception support implementation.
 */

/*
 * Copyright (c) 2018 embedded brains GmbH

 * Copyright (c) 2015 University of York.
 * Hesham Almatary <hesham@alumni.york.ac.uk>
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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <rtems/asm.h>
#include <rtems/score/percpu.h>

PUBLIC(_RISCV_Exception_handler)

	.section	.text, "ax", @progbits
	.align	2

TYPE_FUNC(_RISCV_Exception_handler)
SYM(_RISCV_Exception_handler):

#ifdef __CHERI__
.option capmode
	cincoffset	csp, csp, -(CPU_INTERRUPT_FRAME_SIZE)

	/* Save */
	csc	  ca0, RISCV_INTERRUPT_FRAME_A0(csp)
	csc	  ca1, RISCV_INTERRUPT_FRAME_A1(csp)
	csc	  ca2, RISCV_INTERRUPT_FRAME_A2(csp)
	csc	  cs0, RISCV_INTERRUPT_FRAME_S0(csp)
	csrr	a0, mcause
	csrr	a1, mstatus
	csrr	a2, mepc
	GET_SELF_CPU_CONTROL	cs0
	csc 	cs1, RISCV_INTERRUPT_FRAME_S1(csp)

#if __riscv_flen > 0
	frcsr	s1
#endif

	csc	cra, RISCV_INTERRUPT_FRAME_RA(csp)
	csc	ca3, RISCV_INTERRUPT_FRAME_A3(csp)
	csc	ca4, RISCV_INTERRUPT_FRAME_A4(csp)
	csc	ca5, RISCV_INTERRUPT_FRAME_A5(csp)
	csc	ca6, RISCV_INTERRUPT_FRAME_A6(csp)
	csc	ca7, RISCV_INTERRUPT_FRAME_A7(csp)
	csc	ct0, RISCV_INTERRUPT_FRAME_T0(csp)
	csc	ct1, RISCV_INTERRUPT_FRAME_T1(csp)
	csc	ct2, RISCV_INTERRUPT_FRAME_T2(csp)
	csc	ct3, RISCV_INTERRUPT_FRAME_T3(csp)
	csc	ct4, RISCV_INTERRUPT_FRAME_T4(csp)
	csc	ct5, RISCV_INTERRUPT_FRAME_T5(csp)
	csc	ct6, RISCV_INTERRUPT_FRAME_T6(csp)

  # TODO: csd/csw depending on xlen, but for now assume rv64
	csd	 a1, RISCV_INTERRUPT_FRAME_MSTATUS(csp)
	csd	 a2, RISCV_INTERRUPT_FRAME_MEPC(csp)

#if __riscv_flen > 0
	csw	  s1, RISCV_INTERRUPT_FRAME_FCSR(csp)
	FSREG	ft0, RISCV_INTERRUPT_FRAME_FT0(csp)
	FSREG	ft1, RISCV_INTERRUPT_FRAME_FT1(csp)
	FSREG	ft2, RISCV_INTERRUPT_FRAME_FT2(csp)
	FSREG	ft3, RISCV_INTERRUPT_FRAME_FT3(csp)
	FSREG	ft4, RISCV_INTERRUPT_FRAME_FT4(csp)
	FSREG	ft5, RISCV_INTERRUPT_FRAME_FT5(csp)
	FSREG	ft6, RISCV_INTERRUPT_FRAME_FT6(csp)
	FSREG	ft7, RISCV_INTERRUPT_FRAME_FT7(csp)
	FSREG	ft8, RISCV_INTERRUPT_FRAME_FT8(csp)
	FSREG	ft9, RISCV_INTERRUPT_FRAME_FT9(csp)
	FSREG	ft10, RISCV_INTERRUPT_FRAME_FT10(csp)
	FSREG	ft11, RISCV_INTERRUPT_FRAME_FT11(csp)
	FSREG	fa0, RISCV_INTERRUPT_FRAME_FA0(csp)
	FSREG	fa1, RISCV_INTERRUPT_FRAME_FA1(csp)
	FSREG	fa2, RISCV_INTERRUPT_FRAME_FA2(csp)
	FSREG	fa3, RISCV_INTERRUPT_FRAME_FA3(csp)
	FSREG	fa4, RISCV_INTERRUPT_FRAME_FA4(csp)
	FSREG	fa5, RISCV_INTERRUPT_FRAME_FA5(csp)
	FSREG	fa6, RISCV_INTERRUPT_FRAME_FA6(csp)
	FSREG	fa7, RISCV_INTERRUPT_FRAME_FA7(csp)
#endif

	/* Check if this is a synchronous or interrupt exception */
	bgez	a0, .Lsynchronous_exception

	/* Increment interrupt nest and thread dispatch disable level */
	clw	t0, PER_CPU_ISR_NEST_LEVEL(cs0)
	clw	t1, PER_CPU_THREAD_DISPATCH_DISABLE_LEVEL(cs0)
	addi	t2, t0, 1
	addi	t1, t1, 1
	csw	t2, PER_CPU_ISR_NEST_LEVEL(cs0)
	csw	t1, PER_CPU_THREAD_DISPATCH_DISABLE_LEVEL(cs0)

	// CLEAR_RESERVATIONS	s0

	/*
	 * Remember current stack pointer in non-volatile register s1.  Switch
	 * to interrupt stack if necessary.
	 */
	cmove	cs1, csp
	bnez	t0, .Linterrupt_stack_switch_done
	clc 	csp, PER_CPU_INTERRUPT_STACK_HIGH(cs0)
.Linterrupt_stack_switch_done:

	cmove	ca1, cs0

	#call	_RISCV_Interrupt_dispatch
  clgc              ct0, _RISCV_Interrupt_dispatch
  cjalr             cra, ct0

	/* Load some per-CPU variables */
	clw	t0, PER_CPU_THREAD_DISPATCH_DISABLE_LEVEL(cs0)
	clbu	t1, PER_CPU_DISPATCH_NEEDED(cs0)
	clw	t2, PER_CPU_ISR_DISPATCH_DISABLE(cs0)
	clw	t3, PER_CPU_ISR_NEST_LEVEL(cs0)

	/* Restore stack pointer */
	cmove	csp, cs1

	/* Decrement levels and determine thread dispatch state */
	xor	t1, t1, t0
	addi	t0, t0, -1
	or	t1, t1, t0
	or	t1, t1, t2
	addi	t3, t3, -1

	/* Store thread dispatch disable and ISR nest levels */
	csw	t0, PER_CPU_THREAD_DISPATCH_DISABLE_LEVEL(cs0)
	csw	t3, PER_CPU_ISR_NEST_LEVEL(cs0)

	/*
	 * Check thread dispatch necessary, ISR dispatch disable and thread
	 * dispatch disable level.
	 */
	bnez	t1, .Lthread_dispatch_done

.Ldo_thread_dispatch:

	/* Set ISR dispatch disable and thread dispatch disable level to one */
	li	t0, 1
	csw	t0, PER_CPU_ISR_DISPATCH_DISABLE(cs0)
	csw	t0, PER_CPU_THREAD_DISPATCH_DISABLE_LEVEL(cs0)

	/* Call _Thread_Do_dispatch(), this function will enable interrupts */
	cmove	ca0, cs0
	li	a1, RISCV_MSTATUS_MIE

	#call	_Thread_Do_dispatch
  clgc              ct0, _Thread_Do_dispatch
  cjalr             cra, ct0

	/* Disable interrupts */
	csrrc	zero, mstatus, RISCV_MSTATUS_MIE

	GET_SELF_CPU_CONTROL	cs0

	/* Check if we have to do the thread dispatch again */
	clbu	t0, PER_CPU_DISPATCH_NEEDED(cs0)
	bnez	t0, .Ldo_thread_dispatch

	/* We are done with thread dispatching */
	csw	zero, PER_CPU_ISR_DISPATCH_DISABLE(cs0)

.Lthread_dispatch_done:

	/* Restore */
	cld	a0, RISCV_INTERRUPT_FRAME_MSTATUS(csp)
	cld	a1, RISCV_INTERRUPT_FRAME_MEPC(csp)

	clc	ca2, RISCV_INTERRUPT_FRAME_A2(csp)
	clc	cs0, RISCV_INTERRUPT_FRAME_S0(csp)
	clc	cs1, RISCV_INTERRUPT_FRAME_S1(csp)
	clc	cra, RISCV_INTERRUPT_FRAME_RA(csp)
	clc	ca3, RISCV_INTERRUPT_FRAME_A3(csp)
	clc	ca4, RISCV_INTERRUPT_FRAME_A4(csp)
	clc	ca5, RISCV_INTERRUPT_FRAME_A5(csp)
	clc	ca6, RISCV_INTERRUPT_FRAME_A6(csp)
	clc	ca7, RISCV_INTERRUPT_FRAME_A7(csp)
	clc	ct0, RISCV_INTERRUPT_FRAME_T0(csp)
	clc	ct1, RISCV_INTERRUPT_FRAME_T1(csp)
	clc	ct2, RISCV_INTERRUPT_FRAME_T2(csp)
	clc	ct3, RISCV_INTERRUPT_FRAME_T3(csp)
	clc	ct4, RISCV_INTERRUPT_FRAME_T4(csp)
	clc	ct5, RISCV_INTERRUPT_FRAME_T5(csp)
	clc	ct6, RISCV_INTERRUPT_FRAME_T6(csp)
	csrw	mstatus, a0
	csrw	mepc, a1

  cspecialrw ca0, pcc, cnull
  csetoffset ca0, ca0, a1
  cspecialrw cnull, mepcc, ca0

#if __riscv_flen > 0
	clw	a0, RISCV_INTERRUPT_FRAME_FCSR(csp)
	FLREG	ft0, RISCV_INTERRUPT_FRAME_FT0(csp)
	FLREG	ft1, RISCV_INTERRUPT_FRAME_FT1(csp)
	FLREG	ft2, RISCV_INTERRUPT_FRAME_FT2(csp)
	FLREG	ft3, RISCV_INTERRUPT_FRAME_FT3(csp)
	FLREG	ft4, RISCV_INTERRUPT_FRAME_FT4(csp)
	FLREG	ft5, RISCV_INTERRUPT_FRAME_FT5(csp)
	FLREG	ft6, RISCV_INTERRUPT_FRAME_FT6(csp)
	FLREG	ft7, RISCV_INTERRUPT_FRAME_FT7(csp)
	FLREG	ft8, RISCV_INTERRUPT_FRAME_FT8(csp)
	FLREG	ft9, RISCV_INTERRUPT_FRAME_FT9(csp)
	FLREG	ft10, RISCV_INTERRUPT_FRAME_FT10(csp)
	FLREG	ft11, RISCV_INTERRUPT_FRAME_FT11(csp)
	FLREG	fa0, RISCV_INTERRUPT_FRAME_FA0(csp)
	FLREG	fa1, RISCV_INTERRUPT_FRAME_FA1(csp)
	FLREG	fa2, RISCV_INTERRUPT_FRAME_FA2(csp)
	FLREG	fa3, RISCV_INTERRUPT_FRAME_FA3(csp)
	FLREG	fa4, RISCV_INTERRUPT_FRAME_FA4(csp)
	FLREG	fa5, RISCV_INTERRUPT_FRAME_FA5(csp)
	FLREG	fa6, RISCV_INTERRUPT_FRAME_FA6(csp)
	FLREG	fa7, RISCV_INTERRUPT_FRAME_FA7(csp)
	fscsr	a0
#endif

	clc	ca0, RISCV_INTERRUPT_FRAME_A0(csp)
	clc	ca1, RISCV_INTERRUPT_FRAME_A1(csp)

	cincoffset	csp, csp, CPU_INTERRUPT_FRAME_SIZE

	mret
#else
	addi	sp, sp, -CPU_INTERRUPT_FRAME_SIZE

	/* Save */
	SREG	a0, RISCV_INTERRUPT_FRAME_A0(sp)
	SREG	a1, RISCV_INTERRUPT_FRAME_A1(sp)
	SREG	a2, RISCV_INTERRUPT_FRAME_A2(sp)
	SREG	s0, RISCV_INTERRUPT_FRAME_S0(sp)
	csrr	a0, mcause
	csrr	a1, mstatus
	csrr	a2, mepc
	GET_SELF_CPU_CONTROL	s0
	SREG	s1, RISCV_INTERRUPT_FRAME_S1(sp)
#if __riscv_flen > 0
	frcsr	s1
#endif
	SREG	ra, RISCV_INTERRUPT_FRAME_RA(sp)
	SREG	a3, RISCV_INTERRUPT_FRAME_A3(sp)
	SREG	a4, RISCV_INTERRUPT_FRAME_A4(sp)
	SREG	a5, RISCV_INTERRUPT_FRAME_A5(sp)
	SREG	a6, RISCV_INTERRUPT_FRAME_A6(sp)
	SREG	a7, RISCV_INTERRUPT_FRAME_A7(sp)
	SREG	t0, RISCV_INTERRUPT_FRAME_T0(sp)
	SREG	t1, RISCV_INTERRUPT_FRAME_T1(sp)
	SREG	t2, RISCV_INTERRUPT_FRAME_T2(sp)
	SREG	t3, RISCV_INTERRUPT_FRAME_T3(sp)
	SREG	t4, RISCV_INTERRUPT_FRAME_T4(sp)
	SREG	t5, RISCV_INTERRUPT_FRAME_T5(sp)
	SREG	t6, RISCV_INTERRUPT_FRAME_T6(sp)
	SREG	a1, RISCV_INTERRUPT_FRAME_MSTATUS(sp)
	SREG	a2, RISCV_INTERRUPT_FRAME_MEPC(sp)
#if __riscv_flen > 0
	sw	s1, RISCV_INTERRUPT_FRAME_FCSR(sp)
	FSREG	ft0, RISCV_INTERRUPT_FRAME_FT0(sp)
	FSREG	ft1, RISCV_INTERRUPT_FRAME_FT1(sp)
	FSREG	ft2, RISCV_INTERRUPT_FRAME_FT2(sp)
	FSREG	ft3, RISCV_INTERRUPT_FRAME_FT3(sp)
	FSREG	ft4, RISCV_INTERRUPT_FRAME_FT4(sp)
	FSREG	ft5, RISCV_INTERRUPT_FRAME_FT5(sp)
	FSREG	ft6, RISCV_INTERRUPT_FRAME_FT6(sp)
	FSREG	ft7, RISCV_INTERRUPT_FRAME_FT7(sp)
	FSREG	ft8, RISCV_INTERRUPT_FRAME_FT8(sp)
	FSREG	ft9, RISCV_INTERRUPT_FRAME_FT9(sp)
	FSREG	ft10, RISCV_INTERRUPT_FRAME_FT10(sp)
	FSREG	ft11, RISCV_INTERRUPT_FRAME_FT11(sp)
	FSREG	fa0, RISCV_INTERRUPT_FRAME_FA0(sp)
	FSREG	fa1, RISCV_INTERRUPT_FRAME_FA1(sp)
	FSREG	fa2, RISCV_INTERRUPT_FRAME_FA2(sp)
	FSREG	fa3, RISCV_INTERRUPT_FRAME_FA3(sp)
	FSREG	fa4, RISCV_INTERRUPT_FRAME_FA4(sp)
	FSREG	fa5, RISCV_INTERRUPT_FRAME_FA5(sp)
	FSREG	fa6, RISCV_INTERRUPT_FRAME_FA6(sp)
	FSREG	fa7, RISCV_INTERRUPT_FRAME_FA7(sp)
#endif

	/* Check if this is a synchronous or interrupt exception */
	bgez	a0, .Lsynchronous_exception

	/* Increment interrupt nest and thread dispatch disable level */
	lw	t0, PER_CPU_ISR_NEST_LEVEL(s0)
	lw	t1, PER_CPU_THREAD_DISPATCH_DISABLE_LEVEL(s0)
	addi	t2, t0, 1
	addi	t1, t1, 1
	sw	t2, PER_CPU_ISR_NEST_LEVEL(s0)
	sw	t1, PER_CPU_THREAD_DISPATCH_DISABLE_LEVEL(s0)

	CLEAR_RESERVATIONS	s0

	/*
	 * Remember current stack pointer in non-volatile register s1.  Switch
	 * to interrupt stack if necessary.
	 */
	mv	s1, sp
	bnez	t0, .Linterrupt_stack_switch_done
	LREG	sp, PER_CPU_INTERRUPT_STACK_HIGH(s0)
.Linterrupt_stack_switch_done:

	mv	a1, s0
	call	_RISCV_Interrupt_dispatch

	/* Load some per-CPU variables */
	lw	t0, PER_CPU_THREAD_DISPATCH_DISABLE_LEVEL(s0)
	lbu	t1, PER_CPU_DISPATCH_NEEDED(s0)
	lw	t2, PER_CPU_ISR_DISPATCH_DISABLE(s0)
	lw	t3, PER_CPU_ISR_NEST_LEVEL(s0)

	/* Restore stack pointer */
	mv	sp, s1

	/* Decrement levels and determine thread dispatch state */
	xor	t1, t1, t0
	addi	t0, t0, -1
	or	t1, t1, t0
	or	t1, t1, t2
	addi	t3, t3, -1

	/* Store thread dispatch disable and ISR nest levels */
	sw	t0, PER_CPU_THREAD_DISPATCH_DISABLE_LEVEL(s0)
	sw	t3, PER_CPU_ISR_NEST_LEVEL(s0)

	/*
	 * Check thread dispatch necessary, ISR dispatch disable and thread
	 * dispatch disable level.
	 */
	bnez	t1, .Lthread_dispatch_done

.Ldo_thread_dispatch:

	/* Set ISR dispatch disable and thread dispatch disable level to one */
	li	t0, 1
	sw	t0, PER_CPU_ISR_DISPATCH_DISABLE(s0)
	sw	t0, PER_CPU_THREAD_DISPATCH_DISABLE_LEVEL(s0)

	/* Call _Thread_Do_dispatch(), this function will enable interrupts */
	mv	a0, s0
	li	a1, RISCV_MSTATUS_MIE
	call	_Thread_Do_dispatch

	/* Disable interrupts */
	csrrc	zero, mstatus, RISCV_MSTATUS_MIE

#ifdef RTEMS_SMP
	GET_SELF_CPU_CONTROL	s0
#endif

	/* Check if we have to do the thread dispatch again */
	lbu	t0, PER_CPU_DISPATCH_NEEDED(s0)
	bnez	t0, .Ldo_thread_dispatch

	/* We are done with thread dispatching */
	sw	zero, PER_CPU_ISR_DISPATCH_DISABLE(s0)

.Lthread_dispatch_done:

	/* Restore */
	LREG	a0, RISCV_INTERRUPT_FRAME_MSTATUS(sp)
	LREG	a1, RISCV_INTERRUPT_FRAME_MEPC(sp)
	LREG	a2, RISCV_INTERRUPT_FRAME_A2(sp)
	LREG	s0, RISCV_INTERRUPT_FRAME_S0(sp)
	LREG	s1, RISCV_INTERRUPT_FRAME_S1(sp)
	LREG	ra, RISCV_INTERRUPT_FRAME_RA(sp)
	LREG	a3, RISCV_INTERRUPT_FRAME_A3(sp)
	LREG	a4, RISCV_INTERRUPT_FRAME_A4(sp)
	LREG	a5, RISCV_INTERRUPT_FRAME_A5(sp)
	LREG	a6, RISCV_INTERRUPT_FRAME_A6(sp)
	LREG	a7, RISCV_INTERRUPT_FRAME_A7(sp)
	LREG	t0, RISCV_INTERRUPT_FRAME_T0(sp)
	LREG	t1, RISCV_INTERRUPT_FRAME_T1(sp)
	LREG	t2, RISCV_INTERRUPT_FRAME_T2(sp)
	LREG	t3, RISCV_INTERRUPT_FRAME_T3(sp)
	LREG	t4, RISCV_INTERRUPT_FRAME_T4(sp)
	LREG	t5, RISCV_INTERRUPT_FRAME_T5(sp)
	LREG	t6, RISCV_INTERRUPT_FRAME_T6(sp)
	csrw	mstatus, a0
	csrw	mepc, a1
#if __riscv_flen > 0
	lw	a0, RISCV_INTERRUPT_FRAME_FCSR(sp)
	FLREG	ft0, RISCV_INTERRUPT_FRAME_FT0(sp)
	FLREG	ft1, RISCV_INTERRUPT_FRAME_FT1(sp)
	FLREG	ft2, RISCV_INTERRUPT_FRAME_FT2(sp)
	FLREG	ft3, RISCV_INTERRUPT_FRAME_FT3(sp)
	FLREG	ft4, RISCV_INTERRUPT_FRAME_FT4(sp)
	FLREG	ft5, RISCV_INTERRUPT_FRAME_FT5(sp)
	FLREG	ft6, RISCV_INTERRUPT_FRAME_FT6(sp)
	FLREG	ft7, RISCV_INTERRUPT_FRAME_FT7(sp)
	FLREG	ft8, RISCV_INTERRUPT_FRAME_FT8(sp)
	FLREG	ft9, RISCV_INTERRUPT_FRAME_FT9(sp)
	FLREG	ft10, RISCV_INTERRUPT_FRAME_FT10(sp)
	FLREG	ft11, RISCV_INTERRUPT_FRAME_FT11(sp)
	FLREG	fa0, RISCV_INTERRUPT_FRAME_FA0(sp)
	FLREG	fa1, RISCV_INTERRUPT_FRAME_FA1(sp)
	FLREG	fa2, RISCV_INTERRUPT_FRAME_FA2(sp)
	FLREG	fa3, RISCV_INTERRUPT_FRAME_FA3(sp)
	FLREG	fa4, RISCV_INTERRUPT_FRAME_FA4(sp)
	FLREG	fa5, RISCV_INTERRUPT_FRAME_FA5(sp)
	FLREG	fa6, RISCV_INTERRUPT_FRAME_FA6(sp)
	FLREG	fa7, RISCV_INTERRUPT_FRAME_FA7(sp)
	fscsr	a0
#endif
	LREG	a0, RISCV_INTERRUPT_FRAME_A0(sp)
	LREG	a1, RISCV_INTERRUPT_FRAME_A1(sp)

	addi	sp, sp, (CPU_INTERRUPT_FRAME_SIZE)

	mret
#endif /* __CHERI__ */

.Lsynchronous_exception:

#ifdef __CHERI__
	csd a0, RISCV_EXCEPTION_FRAME_MCAUSE(csp)
  cincoffset ca0, csp, CPU_INTERRUPT_FRAME_SIZE
	csc	ca0, RISCV_EXCEPTION_FRAME_SP(csp)
	csc	cgp, RISCV_EXCEPTION_FRAME_GP(csp)
	csc	ctp, RISCV_EXCEPTION_FRAME_TP(csp)
	csc	cs2, RISCV_EXCEPTION_FRAME_S2(csp)
	csc	cs3, RISCV_EXCEPTION_FRAME_S3(csp)
	csc	cs4, RISCV_EXCEPTION_FRAME_S4(csp)
	csc	cs5, RISCV_EXCEPTION_FRAME_S5(csp)
	csc	cs6, RISCV_EXCEPTION_FRAME_S6(csp)
	csc	cs7, RISCV_EXCEPTION_FRAME_S7(csp)
	csc	cs8, RISCV_EXCEPTION_FRAME_S8(csp)
	csc	cs9, RISCV_EXCEPTION_FRAME_S9(csp)
	csc	cs10, RISCV_EXCEPTION_FRAME_S10(csp)
	csc	cs11, RISCV_EXCEPTION_FRAME_S11(csp)
#if __riscv_flen > 0
	FSREG	fs0, RISCV_EXCEPTION_FRAME_FS0(csp)
	FSREG	fs1, RISCV_EXCEPTION_FRAME_FS1(csp)
	FSREG	fs2, RISCV_EXCEPTION_FRAME_FS2(csp)
	FSREG	fs3, RISCV_EXCEPTION_FRAME_FS3(csp)
	FSREG	fs4, RISCV_EXCEPTION_FRAME_FS4(csp)
	FSREG	fs5, RISCV_EXCEPTION_FRAME_FS5(csp)
	FSREG	fs6, RISCV_EXCEPTION_FRAME_FS6(csp)
	FSREG	fs7, RISCV_EXCEPTION_FRAME_FS7(csp)
	FSREG	fs8, RISCV_EXCEPTION_FRAME_FS8(csp)
	FSREG	fs9, RISCV_EXCEPTION_FRAME_FS9(csp)
	FSREG	fs10, RISCV_EXCEPTION_FRAME_FS10(csp)
	FSREG	fs11, RISCV_EXCEPTION_FRAME_FS11(csp)
#endif

	li	a0, 9
  cmove ca1, csp

  clgc ct0, _Terminate
  cjr  ct0

#else
	SREG	a0, RISCV_EXCEPTION_FRAME_MCAUSE(sp)
	addi	a0, sp, CPU_INTERRUPT_FRAME_SIZE
	SREG	a0, RISCV_EXCEPTION_FRAME_SP(sp)
	SREG	gp, RISCV_EXCEPTION_FRAME_GP(sp)
	SREG	tp, RISCV_EXCEPTION_FRAME_TP(sp)
	SREG	s2, RISCV_EXCEPTION_FRAME_S2(sp)
	SREG	s3, RISCV_EXCEPTION_FRAME_S3(sp)
	SREG	s4, RISCV_EXCEPTION_FRAME_S4(sp)
	SREG	s5, RISCV_EXCEPTION_FRAME_S5(sp)
	SREG	s6, RISCV_EXCEPTION_FRAME_S6(sp)
	SREG	s7, RISCV_EXCEPTION_FRAME_S7(sp)
	SREG	s8, RISCV_EXCEPTION_FRAME_S8(sp)
	SREG	s9, RISCV_EXCEPTION_FRAME_S9(sp)
	SREG	s10, RISCV_EXCEPTION_FRAME_S10(sp)
	SREG	s11, RISCV_EXCEPTION_FRAME_S11(sp)
#if __riscv_flen > 0
	FSREG	fs0, RISCV_EXCEPTION_FRAME_FS0(sp)
	FSREG	fs1, RISCV_EXCEPTION_FRAME_FS1(sp)
	FSREG	fs2, RISCV_EXCEPTION_FRAME_FS2(sp)
	FSREG	fs3, RISCV_EXCEPTION_FRAME_FS3(sp)
	FSREG	fs4, RISCV_EXCEPTION_FRAME_FS4(sp)
	FSREG	fs5, RISCV_EXCEPTION_FRAME_FS5(sp)
	FSREG	fs6, RISCV_EXCEPTION_FRAME_FS6(sp)
	FSREG	fs7, RISCV_EXCEPTION_FRAME_FS7(sp)
	FSREG	fs8, RISCV_EXCEPTION_FRAME_FS8(sp)
	FSREG	fs9, RISCV_EXCEPTION_FRAME_FS9(sp)
	FSREG	fs10, RISCV_EXCEPTION_FRAME_FS10(sp)
	FSREG	fs11, RISCV_EXCEPTION_FRAME_FS11(sp)
#endif

	li	a0, 9
	mv	a1, sp
	call	_Terminate
#endif /* __CHERI__ */
