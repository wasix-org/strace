/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Direct i64 slots coexist with ILP32 pointers and split pread64 offsets. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>

int
main(void)
{
	char buf[8];
	const off_t big = INT64_C(0x123456789);
	int fd = open("/tmp/strace-slots", O_RDWR | O_CREAT | O_TRUNC, 0600);
	if (fd < 0 || write(fd, "x", 1) != 1)
		return 1;
	if (lseek(fd, big, SEEK_SET) != big ||
	    lseek(fd, -1, SEEK_CUR) != big - 1 ||
	    pread(fd, buf, sizeof(buf), big) != 0)
		return 2;
	errno = 0;
	if (pread(fd, (void *) 1, 1, 0) != -1 || errno != EFAULT)
		return 3;
	/* Invalid flags avoid allocating or extending a multi-gigabyte file. */
	errno = 0;
	if (mmap(NULL, 65536, PROT_READ, 0, fd, INT64_C(0x123450000)) !=
	    MAP_FAILED || errno != EINVAL)
		return 4;
	close(fd);
	unlink("/tmp/strace-slots");
	puts("scalar slots ok");
	return 0;
}
