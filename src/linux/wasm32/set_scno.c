/* SPDX-License-Identifier: LGPL-2.1-or-later */

static int
arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)
{
	errno = EIO;
	return -1;
}
