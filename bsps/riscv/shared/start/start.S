/*
 * Copyright (c) 2018 embedded brains GmbH

 * Copyright (c) 2015 University of York.
 * Hesham Almatary <hesham@alumni.york.ac.uk>
 *
 * Copyright (c) 2013, The Regents of the University of California (Regents).
 * All Rights Reserved.
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

#include <rtems/asm.h>
#include <rtems/score/percpu.h>
#include <rtems/score/riscv-utility.h>
#include <bsp/linker-symbols.h>
#include <bspopts.h>


PUBLIC(_start)
#ifdef __CHERI__
.option nocapmode
#endif /* __CHERI__ */

	.section	.bsp_start_text, "wax", @progbits
	.align	2

TYPE_FUNC(_start)
SYM(_start):

#ifdef __CHERI__
.option capmode
# W^X for PCC and DDC
  cspecialrw      ct0, ddc, cnull
  li              t1, (1<<1)
  not             t1, t1
  candperm        ct0, ct0, t1
  cspecialrw      cnull, ddc, ct0

  cspecialrw      ct0, pcc, cnull
  li              t1, ((1<<3) | (1<<5))
  not             t1, t1
  candperm        ct0, ct0, t1
  LADDR           ct2, 1f
  csetoffset      ct0, ct0, t2
  cjr             ct0
1:
	/* Load global pointer */
	.option	push
	.option	norelax
	LADDR	 cgp, __global_pointer$
	.option	pop

	/* Set exception handler */
	LADDR	ct0, _RISCV_Exception_handler
	csrw	mtvec, t0
#else
	/* Load global pointer */
	.option	push
	.option	norelax
	LADDR	gp, __global_pointer$
	.option	pop

	/* Set exception handler */
	LADDR	t0, _RISCV_Exception_handler
	csrw	mtvec, t0
#endif /* __CHERI__ */

	/* Init FPU */
#ifdef __riscv_flen
	li	t0, MSTATUS_FS
	csrs	mstatus, t0
	csrw	fcsr, zero
#endif

	/* Load stack pointer and branch to secondary processor start if necessary */

#if __CHERI__
#ifdef RTEMS_SMP
#error "No support for SMP in CHERI mode yet"
#endif /* RTEMS_SMP */

  /* Move a1 (DTB address) to s0 (callee saved) for later use */
  mv              s0, a1

  /* Setup the stack */
  LADDR            ct1, _ISR_Stack_area_end
  LADDR            ct0, _ISR_Stack_area_begin
  sub             t2, t1, t0
  cfromptr        csp, ddc, t0
  csetbounds      csp, csp, t2
  csetoffset      csp, csp, t2

  /* From now on, run in purecap mode */
  cspecialrw      ct0, pcc, cnull
  LADDR           ct1, purecap
  csetaddr        ct0, ct0, t1
  li              t1, 1
  csetflags       ct0, ct0, t1
  cjr             ct0

purecap:
  /* Initialise the captable. */
  LADDR           ct1, riscv_cheri_init_globals
  csetaddr        ct0, ct0, t1
  cjalr           cra, ct0

  /* Pin _Per_CPU_Information to mscratchc. It is used in context switching
   * and interrupt handling
   */
	clgc	          ct2, _Per_CPU_Information
  cspecialrw      cnull, mscratchc, ct2

#ifdef BSP_START_COPY_FDT_FROM_U_BOOT
	mv	            a0, s0
  cfromptr        ca0, ddc, s0
  clgc            ct0, bsp_fdt_copy
  cjalr           cra, ct0
#endif
.option nocapmode

	/* Clear .bss */
	LADDR	         a0, bsp_section_bss_begin
	cfromptr	     ca0, ddc, a0
	li	           a1, 0
	LADDR 	       a2, bsp_section_bss_size
	csetbounds     ca0, ca0, a2
  LADDR          t1, memset
  csetoffset     ct0, ct0, t1
  cjalr          cra, ct0

#ifdef RTEMS_SMP
	/* Give go to secondary processors */
	LADDR	t0, .Lsecondary_processor_go
	fence	iorw,ow
	amoswap.w	zero, zero, 0(t0)
#endif

.option capmode
	/* Setup CHERI trap code cap */
  clgc            ct2, _RISCV_Exception_handler
  cspecialrw      cnull, mtcc, ct2

  /* Jump to boot_card in purecap mode */
	li	a0, 0
  1:auipcc        ct0, %pcrel_hi(boot_card)
  cincoffset      ct0, ct0, %pcrel_lo(1b)
  cjr ct0
#else

#ifdef RTEMS_SMP
	LADDR	sp, _ISR_Stack_area_begin
	LADDR	t2, _ISR_Stack_size
	csrr	s0, mhartid
	LADDR	t0, _Per_CPU_Information
	slli	t1, s0, PER_CPU_CONTROL_SIZE_LOG2
	add	s1, t0, t1
	csrw	mscratch, s1
	bnez	s0, .Lstart_on_secondary_processor
	add	sp, sp, t2
#else
	LADDR	sp, _ISR_Stack_area_end
#endif

#ifdef BSP_START_COPY_FDT_FROM_U_BOOT
	mv	a0, a1
	call	bsp_fdt_copy
#endif

	/* Clear .bss */
	LADDR	a0, bsp_section_bss_begin
	li	a1, 0
	LADDR	a2, bsp_section_bss_size
	call	memset

#ifdef RTEMS_SMP
	/* Give go to secondary processors */
	LADDR	t0, .Lsecondary_processor_go
	fence	iorw,ow
	amoswap.w	zero, zero, 0(t0)
#endif

	li	a0, 0
	j	boot_card
#endif /* __CHERI__ */

#ifdef RTEMS_SMP

.Lstart_on_secondary_processor:

	/* Adjust stack pointer */
#ifdef __riscv_mul
	addi	t0, s0, 1
	mul	t2, t2, t0
#else
	mv	t0, s0
	mv	t3, t2

.Ladd_more:

	add	t2, t2, t3
	addi	t0, t0, -1
	bnez	t0, .Ladd_more
#endif
	add	sp, sp, t2

	/* Wait for go issued by the boot processor (mhartid == 0) */
	LADDR	t0, .Lsecondary_processor_go

.Lwait_for_go_again:

	lw	t1, 0(t0)
	fence	iorw, iorw
	bnez	t1, .Lwait_for_go_again

	mv	a0, s1
	call	bsp_start_on_secondary_processor

#if __riscv_xlen == 32
	.align	2
#elif __riscv_xlen == 64
	.align	3
#endif

.Lsecondary_processor_go:

	/*
	 * These are ebreak instructions, just in case we end up here executing
	 * code.
	 */
	.word	0x00100073
#if __riscv_xlen == 64
	.word	0x00100073
#endif

#endif /* RTEMS_SMP */

#ifdef __CHERI__
.option capmode
#endif /* __CHERI__ */
