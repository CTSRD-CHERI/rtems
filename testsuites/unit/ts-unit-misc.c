/* SPDX-License-Identifier: BSD-2-Clause */

/*
 * Copyright (C) 2019 embedded brains GmbH (http://www.embedded-brains.de)
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
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include <t.h>

#include <tmacros.h>

const char rtems_test_name[] = "UNITMISC";

static char buffer[512];

static const T_action actions[] = {
	T_report_hash_sha256,
	T_check_task_context,
	T_check_file_descriptors,
	T_check_rtems_barriers,
	T_check_rtems_extensions,
	T_check_rtems_message_queues,
	T_check_rtems_partitions,
	T_check_rtems_periods,
	T_check_rtems_regions,
	T_check_rtems_semaphores,
	T_check_rtems_tasks,
	T_check_rtems_timers,
	T_check_posix_keys
};

static const T_config config = {
	.name = "UnitMisc",
	.buf = buffer,
	.buf_size = sizeof(buffer),
	.putchar = T_putchar_default,
	.verbosity = T_VERBOSE,
	.now = T_now_clock,
	.action_count = T_ARRAY_SIZE(actions),
	.actions = actions
};

static void
Init(rtems_task_argument arg)
{
	(void)arg;

	TEST_BEGIN();
	T_register();

	if (T_main(&config) == 0) {
		TEST_END();
	}

	rtems_test_exit(0);
}

#define CONFIGURE_APPLICATION_NEEDS_CLOCK_DRIVER

#define CONFIGURE_UNLIMITED_OBJECTS

#define CONFIGURE_UNIFIED_WORK_AREAS

#define CONFIGURE_INIT_TASK_ATTRIBUTES RTEMS_FLOATING_POINT

#define CONFIGURE_RTEMS_INIT_TASKS_TABLE

#define CONFIGURE_INIT

#include <rtems/confdefs.h>
