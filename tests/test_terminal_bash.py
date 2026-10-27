"""PTY smoke tests for the interactive Bash screens (Unix only)."""

import os
import re
import select
import signal
import struct
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

if os.name == "posix":
    import fcntl
    import pty
    import termios


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "posix", "PTY requires Unix")
class TerminalBashTests(unittest.TestCase):
    def run_screen(self, argv, initial=(8, 3), resized=(20, 5)):
        with tempfile.TemporaryDirectory() as scratch:
            master, slave = pty.openpty()

            def size(cols, rows):
                fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))

            def frame(timeout=8):
                data = b""
                end = time.monotonic() + timeout
                while time.monotonic() < end:
                    if select.select([master], [], [], 0.1)[0]:
                        try:
                            data += os.read(master, 65536)
                        except OSError:
                            break
                    if b"\x1b[H" in data and b"\x1b[J" in data.split(b"\x1b[H")[-1]:
                        break
                self.assertIn(b"\x1b[J", data, data[-200:])
                raw = data.split(b"\x1b[H")[-1].split(b"\x1b[J")[0]
                text = re.sub(rb"\x1b\[[0-9;?]*[A-Za-z]", b"", raw).decode(errors="replace")
                return text.splitlines()

            size(*initial)
            env = dict(os.environ, TERM="xterm-256color", NO_COLOR="1",
                       GOODPOMO_DIR=str(Path(scratch) / "pomo"), GOODPOMO_SEM_ANIM="1",
                       XDG_CONFIG_HOME=str(Path(scratch) / "config"),
                       XDG_DATA_HOME=str(Path(scratch) / "data"))
            proc = subprocess.Popen(argv, cwd=ROOT, stdin=slave, stdout=slave, stderr=slave, env=env)
            try:
                before = frame()
                size(*resized)
                os.kill(proc.pid, signal.SIGWINCH)
                after = frame()
                for lines, (cols, rows) in ((before, initial), (after, resized)):
                    self.assertLessEqual(len(lines), rows, lines)
                    self.assertTrue(all(len(line) <= cols for line in lines), lines)
                os.write(master, b"q")
                proc.wait(timeout=8)
                self.assertEqual(proc.returncode, 0)
                return before, after
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()
                os.close(master)
                os.close(slave)

    def test_setup_resizes(self):
        self.run_screen(["bash", "setup.sh"], resized=(52, 16))

    def test_goodrepo_resizes(self):
        self.run_screen(["bash", "goodrepo/goodrepo", "-C", "."], resized=(52, 16))

    def test_goodpomo_resizes(self):
        self.run_screen(["bash", "goodpomo/goodpomo", "foco", "1"], resized=(52, 16))

    def test_one_cell_menu(self):
        self.run_screen(["bash", "goodrepo/goodrepo", "-C", "."], initial=(1, 1))


if __name__ == "__main__":
    unittest.main()
