#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Focused wasm32 tracing tests. Arguments: RELEASE_CLI GUEST_BIN_DIR OUTPUT_DIR."""
import os
from pathlib import Path
import re
import subprocess
import sys

wasmer, bindir, outdir = map(lambda s: Path(s).resolve(), sys.argv[1:])
outdir.mkdir(parents=True, exist_ok=True)
work = outdir / "work"
work.mkdir(exist_ok=True)
(work / "strace-input").write_text("trace-data\n")
base = [str(wasmer), "run",
        "--compiler-threads", "3", "--no-tty", "--user", "0",
        "--volume", f"{bindir}:/bin", "--volume", f"{work}:/work"]


def run(name, argv, status=0):
    p = subprocess.run(base + [str(bindir / argv[0]), "--"] + argv[1:],
                       capture_output=True, text=True, timeout=90)
    (outdir / f"{name}.out").write_text(p.stdout)
    (outdir / f"{name}.trace").write_text(p.stderr)
    (outdir / f"{name}.status").write_text(f"{p.returncode}\n")
    assert p.returncode == status, (name, p.returncode, p.stderr[-4000:])
    assert "ptrace_syscall_info.op ==" not in p.stderr, (name, p.stderr)
    print(f"{name}: PASS", flush=True)
    return p.stdout, p.stderr


out, trace = run("ls", ["strace", "-f", "/bin/ls", "/work"])
assert "strace-input" in out
for call in ["execve(", "openat(", "getdents64("]:
    assert call in trace, (call, trace)
assert re.search(r"writev?\(", trace), trace
assert "+++ exited with 0 +++" in trace

out, trace = run("pipe", ["strace", "-f", "/bin/sh", "-c", "echo hi | cat"])
assert out == "hi\n", out
assert len(re.findall(r"\+\+\+ exited with 0 \+\+\+", trace)) == 3, trace
assert len(set(re.findall(r"\[pid\s+(\d+)\]", trace))) >= 2, trace
assert 'execve("/bin/cat"' in trace, trace

out, trace = run("filter", ["strace", "-e", "trace=openat,read",
                            "/bin/cat", "/work/strace-input"])
assert out == "trace-data\n", out
assert 'openat(AT_FDCWD, "/work/strace-input"' in trace
assert '"trace-data\\n"' in trace, trace
assert not re.search(r"^\w+\(", trace.replace("openat(", "(").replace("read(", "("), re.M), trace

out, trace = run("slots", ["strace", "-e", "trace=lseek,pread64,mmap",
                           "/bin/strace-slots"])
assert out == "scalar slots ok\n", out
for pattern in [r"lseek\(\d+, 4886718345, SEEK_SET\)\s+= 4886718345",
                r"lseek\(\d+, -1, SEEK_CUR\)\s+= 4886718344",
                r"pread64\(\d+, .*?, 8, 4886718345\)\s+= 0",
                r"pread64\(\d+, 0x1, 1, 0\)\s+= -1 EFAULT",
                r"mmap\(NULL, 65536, PROT_READ, .*?, \d+, 0x123450000\)\s+= -1 EINVAL"]:
    assert re.search(pattern, trace), (pattern, trace)

out, trace = run("slots-raw", ["strace", "-e", "trace=lseek", "-e", "raw=lseek",
                               "/bin/strace-slots"])
assert re.search(r"lseek\(.*0x123456789.*\)\s+= 0x123456789", trace), trace

out, trace = run("signal", ["strace", "-f", "/bin/sh", "-c",
                            "trap 'echo signal' USR1; kill -USR1 $$; echo done"])
assert out == "signal\ndone\n", out
assert "--- SIGUSR1" in trace, trace

out, trace = run("no-regset", ["disable_ptrace_getregset", "/bin/strace", "-f", "/bin/ls", "/work"])
assert "strace-input" in out and "getdents64(" in trace, trace
_, trace = run("no-info", ["disable_ptrace_get_syscall_info", "/bin/strace", "/bin/ls"], 1)
assert "requires PTRACE_GET_SYSCALL_INFO" in trace, trace
_, trace = run("no-inject", ["strace", "-e", "inject=read:error=EIO", "/bin/ls"], 1)
assert "Register tampering is not supported" in trace, trace
_, trace = run("no-unwind", ["strace", "-k", "/bin/ls"], 1)
assert "not supported" in trace, trace
print("All focused WASIX v2 strace checks passed.", flush=True)
