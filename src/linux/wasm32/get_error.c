/* SPDX-License-Identifier: LGPL-2.1-or-later */

static void
arch_get_error(struct tcb *tcp, const bool check_errno)
{
	/* Reached only if a caller violates the syscall-info-only capability. */
	error_msg_and_die("WASIX v2 requires PTRACE_GET_SYSCALL_INFO");
}
