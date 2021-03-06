/*-
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Copyright (c) 2019 Hesham Almatary
 *
 * This software was developed by SRI International and the University of
 * Cambridge Computer Laboratory (Department of Computer Science and
 * Technology) under DARPA contract HR0011-18-C-0016 ("ECATS"), as part of the
 * DARPA SSITH research programme.
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

/**
  * @file
  *
  * @brief CHERI-RISC-V Utility
  */
#if __CHERI__

#include <cheri_init_globals.h>
#include <rtems/score/cheri-utility.h>

inline void *cheri_build_data_cap(size_t address, size_t size, size_t perms) {
  void *returned_cap = __builtin_cheri_global_data_get();
  returned_cap = __builtin_cheri_perms_and(returned_cap, perms);
  returned_cap = __builtin_cheri_offset_set(returned_cap, address);
  returned_cap = __builtin_cheri_bounds_set(returned_cap, size);
  return returned_cap;
}

inline void *cheri_build_code_cap(size_t address, size_t size, size_t perms) {
  void *returned_cap = __builtin_cheri_program_counter_get();
  returned_cap = __builtin_cheri_perms_and(returned_cap, perms);
  returned_cap = __builtin_cheri_offset_set(returned_cap, address);
  returned_cap = __builtin_cheri_bounds_set(returned_cap, size);
  return returned_cap;
}
#endif /* __CHERI__ */
