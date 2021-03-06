#
# Copyright (c) 2006 Martin Decky
# Copyright (c) 2006 Jakub Jermar 
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# - The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

/*
 * This code is originally in asm.S. This is the only function used from that
 * file, so it has been relocated to this new file ofw.S which is not actually
 * located in the HelenOS code base.
 */

#include <arch/stack.h>
#include <boot/register.h>

.register %g2, #scratch
.register %g3, #scratch

.text

.global ofw
ofw:
	save %sp, -STACK_WINDOW_SAVE_AREA_SIZE, %sp
	set ofw_cif, %l0
	ldx [%l0], %l0
	
	rdpr  %pstate, %l1
	and  %l1, ~PSTATE_AM_BIT, %l2
	wrpr  %l2, 0, %pstate
	
	jmpl %l0, %o7
	mov %i0, %o0

  clr %g4     ! correction for gcc's ABI change

	wrpr %l1, 0, %pstate
	
	ret
	restore %o0, 0, %o0
