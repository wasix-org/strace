/* SPDX-License-Identifier: LGPL-2.1-or-later */

/* The ABI uses RISCV32 as its audit transport identity. */
#define PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_RISCV32, 0 }
#define ARCH_SYSCALL_INFO_ONLY 1
#define HAVE_ARCH_TIME32_SYSCALLS 0
#define HAVE_ARCH_OLD_TIME64_SYSCALLS 0
