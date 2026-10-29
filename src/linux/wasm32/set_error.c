/* SPDX-License-Identifier: LGPL-2.1-or-later */

static int
arch_set_error(struct tcb *tcp)
{
	errno = EIO;
	return -1;
}

static int
arch_set_success(struct tcb *tcp)
{
	errno = EIO;
	return -1;
}
