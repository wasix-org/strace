This generator uses the WASIX v2 ABI's public codegen IR at the pinned ABI
commit. Run from the strace source root:

    WASIXV2_WIT=/path/to/wasmer/lib/wasixv2/codegen/wit
    export WASIXV2_WIT
    cargo test --locked --manifest-path maint/wasixv2-syscalls/Cargo.toml
    cargo run --locked --manifest-path maint/wasixv2-syscalls/Cargo.toml -- \
        "$WASIXV2_WIT" > src/linux/wasm32/syscallent.h

Syscall numbers, names, argument counts and split scalar ordering come from
that ABI. The existing strace table supplies decoder names and classifications;
no second syscall-number table is maintained. Unknown decoders use printargs.
Wasm-specific imports without syscall numbers have no invented numbers.

The ptrace transport uses the ABI's AUDIT_ARCH_RISCV32 identity. It preserves
riscv32 register pairs for @merged-i64 parameters (pread/pwrite, truncate,
fallocate/fadvise, etc.), but lseek and mmap have direct 64-bit scalar slots.
The separate syscall scalar typedefs preserve those slots and results without
changing kernel_long_t, pointer layouts, or PEEKDATA's four-byte word size.

The personality requires syscall info. Event stops with INFO_NONE defer decoding;
no GETREGSET/GETREGS fallback exists. Kernel IP zero and shadow SP are reported
as supplied. Register tampering and unwinding are unsupported.

Use the userland-5 validation recipe to build with wasixcc's asyncify sysroot
and run tests/wasm32-slots.c, ordinary ls, a shell pipeline, the openat/read
filter and syscall-info capability rejection inside the WASIX machine.
