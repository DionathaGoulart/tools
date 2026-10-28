import importlib.machinery
import importlib.util
import argparse
import io
import json
import os
import sys
import unittest
from collections import deque
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / "goodmon" / "goodmon"
SPEC = importlib.util.spec_from_loader(
    "goodmon_test", importlib.machinery.SourceFileLoader("goodmon_test", str(PATH))
)
goodmon = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = goodmon
SPEC.loader.exec_module(goodmon)


class Net:
    def __init__(self, sent, recv):
        self.bytes_sent, self.bytes_recv = sent, recv


class FakeProcess:
    info = {"pid": 7, "name": "proc\x1b", "memory_info": SimpleNamespace(rss=40)}

    def __init__(self):
        self.calls = []

    def cpu_percent(self, interval):
        self.calls.append(interval)
        return 12.5


class FakePsutil:
    Error = RuntimeError

    def __init__(self):
        self.calls = []
        self.process = FakeProcess()
        self.network = Net(10, 20)

    def cpu_percent(self, interval, percpu=False):
        self.calls.append((interval, percpu))
        return [10, 20] if percpu else 15

    def net_io_counters(self):
        return self.network

    def process_iter(self, attrs=None):
        return [self.process]

    def virtual_memory(self):
        return SimpleNamespace(total=100, available=30, percent=70)

    def swap_memory(self):
        return SimpleNamespace(total=20, used=5, percent=25)

    def disk_usage(self, disk):
        return SimpleNamespace(total=200, used=50, free=150, percent=25)

    def boot_time(self):
        return 10

    def cpu_count(self):
        return 2


class GoodmonTest(unittest.TestCase):
    def test_network_delta_and_reset(self):
        monitor = goodmon.Monitor(None, "/")
        monitor.psutil = type("P", (), {"net_io_counters": lambda s: Net(100, 200)})()
        with patch.object(goodmon.time, "monotonic", side_effect=(1, 3, 4)):
            self.assertEqual(monitor._network(1)["recv_per_sec"], 0)
            monitor.psutil.net_io_counters = lambda: Net(140, 260)
            self.assertEqual(monitor._network(3)["recv_per_sec"], 30)
            monitor.psutil.net_io_counters = lambda: Net(1, 1)
            self.assertEqual(monitor._network(4)["recv_per_sec"], 0)

    def test_arguments_and_cleaning(self):
        defaults = goodmon.parser().parse_args([])
        self.assertEqual((defaults.sort, defaults.top), ("ram", 5))
        self.assertEqual(goodmon.top_count("0"), 0)
        self.assertEqual(goodmon.clean("x\x1b[31m"), "x?[31m")
        for value in ("0", "-1", "nan", "inf", "abc"):
            with self.subTest(value=value), self.assertRaises(
                argparse.ArgumentTypeError
            ):
                goodmon.positive_float(value)
        with self.assertRaises(argparse.ArgumentTypeError):
            goodmon.top_count("51")

    def test_network_none_is_explicit_unavailable(self):
        monitor = goodmon.Monitor(
            type("P", (), {"net_io_counters": lambda s: None})(), "/"
        )
        self.assertEqual(
            monitor._network(1), {"sent_per_sec": None, "recv_per_sec": None}
        )

    def test_warmup_and_snapshot_collect_global_metrics(self):
        fake = FakePsutil()
        monitor = goodmon.Monitor(fake, "/")
        with patch.object(goodmon.time, "monotonic", side_effect=(1, 2)), patch.object(
            goodmon.time, "time", return_value=70
        ):
            monitor.warmup()
            fake.network = Net(30, 50)
            data = monitor.snapshot()
        self.assertTrue(monitor.warmed)
        self.assertIn((None, False), fake.calls)
        self.assertIn((None, True), fake.calls)
        self.assertEqual(data["memory"]["used"], 70)
        self.assertEqual(data["network"]["recv_per_sec"], 30)
        self.assertEqual(data["processes"][0]["name"], "proc?")

    def test_process_sort_and_limit_is_shared_by_json(self):
        data = {
            "processes": [
                {"name": "a", "cpu": 1, "rss": 9},
                {"name": "b", "cpu": 3, "rss": 2},
            ]
        }
        self.assertEqual(
            [p["name"] for p in goodmon.selected_processes(data, 1, "cpu")], ["b"]
        )
        self.assertEqual(
            [p["name"] for p in goodmon.selected_processes(data, 1, "ram")], ["a"]
        )

    def run_fake(self, argv, tty=False, env=None):
        class Output(io.StringIO):
            def isatty(self):
                return tty

        output = Output()
        with patch.dict(os.environ, env or {}, clear=True), patch.object(
            goodmon, "load_psutil", return_value=FakePsutil()
        ), patch.object(goodmon.time, "sleep") as sleep, redirect_stdout(output):
            status = goodmon.main(argv)
        return status, output.getvalue(), sleep

    def test_plain_tty_modes_never_emit_ansi(self):
        for argv, env in (
            (["--no-color"], {}),
            ([], {"TERM": "dumb"}),
            ([], {"NO_COLOR": ""}),
        ):
            with self.subTest(argv=argv, env=env):
                status, output, _ = self.run_fake(argv, tty=True, env=env)
                self.assertEqual(status, 0)
                self.assertIn("RAM", output)
                self.assertNotIn("\x1b", output)

    def test_json_in_a_tty_is_json_only_and_respects_sampling_interval(self):
        status, output, sleep = self.run_fake(
            ["--json", "--interval", "0.2", "--top", "0"], tty=True
        )
        self.assertEqual(status, 0)
        data = json.loads(output)
        self.assertEqual(data["processes"], [])
        self.assertEqual(data["memory"]["used"], 70)
        self.assertNotIn("\x1b", output)
        sleep.assert_called_once_with(0.2)

    def test_pipe_defaults_to_a_single_plain_snapshot(self):
        status, output, sleep = self.run_fake([])
        self.assertEqual(status, 0)
        self.assertIn("CPU", output)
        self.assertIn("RAM", output)
        self.assertEqual(output.count("proc?"), 1)
        self.assertNotIn("\x1b", output)
        sleep.assert_called_once()

    def test_narrow_color_rows_keep_complete_escapes_and_cell_width(self):
        from retro import largura

        for columns in (20, 40, 60, 80):
            with patch(
                "retro.shutil.get_terminal_size",
                return_value=os.terminal_size((columns, 24)),
            ):
                status, output, _ = self.run_fake(["--once"], tty=True)
            self.assertEqual(status, 0)
            for line in output.splitlines():
                self.assertLessEqual(largura(line), columns)
                self.assertNotIn("\x1b", goodmon.re.sub(r"\x1b\[[0-9;]*m", "", line))
        self.assertEqual(largura(goodmon._fit("進程名稱", 5)), 5)

    def test_live_respects_height_and_plain_override(self):
        from retro import largura

        class Output(io.StringIO):
            def isatty(self):
                return True

        data = goodmon.Monitor(FakePsutil(), "/").snapshot()
        for columns, height in ((1, 1), (8, 3), (20, 8), (40, 12), (80, 8), (80, 13), (80, 24), (120, 24)):
            output = Output()
            with patch("retro.shutil.get_terminal_size", return_value=os.terminal_size((columns, height))), redirect_stdout(output):
                ui = goodmon.Retro(largura_caixa=100)
                history = {"cpu": deque([15]), "ram": deque([70])}
                goodmon.render(ui, data, 8, "cpu", history, live=True)
            lines = output.getvalue().splitlines()
            self.assertLessEqual(len(lines), max(1, height - 1))
            self.assertTrue(all(largura(line) <= columns for line in lines))

    def test_optional_metrics_and_disappearing_process(self):
        fake = FakePsutil()
        with patch.object(fake, "swap_memory", side_effect=RuntimeError), patch.object(
            fake, "disk_usage", side_effect=OSError
        ), patch.object(fake.process, "cpu_percent", side_effect=RuntimeError):
            monitor = goodmon.Monitor(fake, "/")
            monitor.warmup()
            data = monitor.snapshot()
        self.assertIsNone(data["swap"])
        self.assertIsNone(data["disk"])
        self.assertEqual(data["processes"], [])

    def test_local_venv_can_reexec_even_when_python_is_a_symlink(self):
        folder = PATH.parent / ".venv"
        with patch.object(goodmon.Path, "is_file", return_value=True), patch.object(
            goodmon.sys, "prefix", str(folder.parent)
        ), patch.dict(os.environ, {}, clear=True), patch.object(
            goodmon.os, "execve"
        ) as execute:
            goodmon.maybe_reexec_venv()
        execute.assert_called_once()
        self.assertIn(str(folder), execute.call_args.args[0])

    def test_live_exit_restores_terminal_after_keyboard_interrupt(self):
        class TtyOutput(io.StringIO):
            def isatty(self):
                return True

        output = TtyOutput()
        with patch.dict(os.environ, {}, clear=True), patch.object(
            goodmon, "load_psutil", return_value=FakePsutil()
        ), patch.object(goodmon.time, "sleep"), patch.object(
            goodmon, "wait_key", side_effect=KeyboardInterrupt
        ), patch.object(sys.stdin, "isatty", return_value=False), redirect_stdout(
            output
        ):
            status = goodmon.main([])
        self.assertEqual(status, 130)
        self.assertIn("\x1b[?25l", output.getvalue())
        for reset in ("\x1b[?1000l", "\x1b[?1006l", "\x1b[?25h", "\x1b[?1049l"):
            self.assertIn(reset, output.getvalue())

    def test_panel_caps_processes_at_five_but_json_keeps_requested_limit(self):
        processes = [
            {"pid": index, "name": f"task-{index}", "cpu": index * 50, "rss": (8 - index) * 1024}
            for index in range(1, 8)
        ]
        with patch.object(goodmon.Monitor, "_processes", return_value=processes):
            for order, visible in (("ram", range(1, 6)), ("cpu", range(3, 8))):
                with self.subTest(order=order):
                    status, output, _ = self.run_fake(["--once", "--top", "50", "--sort", order])
                    self.assertEqual(status, 0)
                    for index in range(1, 8):
                        self.assertEqual(f"task-{index}" in output, index in visible)
            status, output, _ = self.run_fake(["--json", "--top", "7"])
            self.assertEqual(status, 0)
            self.assertEqual(len(json.loads(output)["processes"]), 7)

    def test_initial_history_does_not_invent_previous_samples(self):
        self.assertEqual(goodmon.sparkline([], 8), " " * 8)
        self.assertEqual(goodmon.sparkline([70], 8)[:7], " " * 7)
        self.assertEqual(len(goodmon.sparkline(list(range(101)), 8)), 8)

    def test_area_graph_shows_low_load_and_preserves_scale(self):
        graph = goodmon.area_graph([1, 100], 5)
        self.assertTrue(all(row[:3] == "   " for row in graph))
        self.assertNotEqual(graph[-1][-2], " ")
        self.assertTrue(all(row[-1] == "█" for row in graph))

    def test_pie_distinguishes_monochrome_slices_and_handles_zero_usage(self):
        processes = [{"cpu": 200, "rss": 200}, {"cpu": 100, "rss": 100}]
        chart = "".join(goodmon.pie(processes, "cpu", False))
        self.assertIn("1", chart)
        self.assertIn("2", chart)
        self.assertNotIn("\x1b", chart)
        zero = "".join(goodmon.pie([{"cpu": 0, "rss": 0}], "cpu", True))
        empty = "".join(goodmon.pie([], "ram", True))
        self.assertNotIn("█", zero)
        self.assertNotIn("█", empty)

    def test_toggling_rerenders_without_resampling_or_extending_history(self):
        class Output(io.StringIO):
            def isatty(self):
                return True

        data = goodmon.Monitor(FakePsutil(), "/").snapshot()
        frames = []
        render = goodmon.render

        def capture(ui, data, top, order, history, live=False):
            frames.append((order, len(history["cpu"]), len(history["ram"])))
            return render(ui, data, top, order, history, live)

        with patch.dict(os.environ, {}, clear=True), patch.object(
            goodmon, "load_psutil", return_value=FakePsutil()
        ), patch.object(goodmon.time, "sleep"), patch.object(
            goodmon.Monitor, "snapshot", return_value=data
        ) as snapshot, patch.object(goodmon, "render", side_effect=capture), patch.object(
            goodmon, "wait_key", side_effect=("c", "m", "q")
        ), patch.object(sys.stdin, "isatty", return_value=False), redirect_stdout(Output()):
            self.assertEqual(goodmon.main(["--interval", "10"]), 0)
        self.assertEqual(snapshot.call_count, 1)
        self.assertEqual(frames, [("ram", 1, 1), ("cpu", 1, 1), ("ram", 1, 1)])

    def test_key_and_resize_events_do_not_postpone_scheduled_samples(self):
        class Output(io.StringIO):
            def isatty(self):
                return True

        clock = [0.0]
        events = iter(((3, "c"), (3, "m"), (5, None), (0, "q")))

        def wait(*_args):
            elapsed, key = next(events)
            clock[0] += elapsed
            return key

        data = goodmon.Monitor(FakePsutil(), "/").snapshot()
        with patch.dict(os.environ, {}, clear=True), patch.object(
            goodmon, "load_psutil", return_value=FakePsutil()
        ), patch.object(goodmon.time, "sleep"), patch.object(
            goodmon.time, "monotonic", side_effect=lambda: clock[0]
        ), patch.object(goodmon.Monitor, "snapshot", return_value=data) as snapshot, patch.object(
            goodmon, "wait_key", side_effect=wait
        ), patch.object(sys.stdin, "isatty", return_value=False), redirect_stdout(Output()):
            self.assertEqual(goodmon.main(["--interval", "10"]), 0)
        self.assertEqual(snapshot.call_count, 2)

    def test_wait_key_returns_on_resize(self):
        with patch.object(sys.stdin, "isatty", return_value=False), patch.object(
            goodmon.time, "sleep"
        ), patch.object(goodmon.os, "get_terminal_size", return_value=os.terminal_size((40, 12))):
            self.assertIsNone(goodmon.wait_key(1, (80, 24)))

    def test_button_bounds_match_visible_controls(self):
        class Output(io.StringIO):
            def isatty(self):
                return True

        data = goodmon.Monitor(FakePsutil(), "/").snapshot()
        for columns, height in ((40, 12), (80, 24), (80, 8), (20, 8), (8, 3)):
            output = Output()
            with patch.dict(os.environ, {}, clear=True), patch(
                "retro.shutil.get_terminal_size", return_value=os.terminal_size((columns, height))
            ), patch.object(sys.stdin, "isatty", return_value=True), redirect_stdout(output):
                ui = goodmon.Retro(largura_caixa=100)
                goodmon.render(ui, data, 5, "ram", {"cpu": deque([15]), "ram": deque([70])}, live=True)
            lines = goodmon.re.sub(r"\x1b\[[0-9;]*m", "", output.getvalue()).splitlines()
            for metric, (left, right, row) in ui.button_bounds.items():
                label = "[M RAM]" if metric == "ram" else "[C CPU]"
                self.assertEqual(lines[row - 1][left - 1:right], label)

    @unittest.skipIf(os.name == "nt", "SGR mouse uses POSIX terminal input")
    def test_sgr_accepts_left_press_only(self):
        import select

        for sequence, expected in (
            (b"c", "c"),
            (b"\x1b[<0;12;8M", "mouse:12:8"),
            (b"\x1b[<0;12;8m", None),
            (b"\x1b[<2;12;8M", None),
            (b"\x1b[<32;12;8M", None),
            (b"\x1b[<64;12;8M", None),
            (b"\x1b[<65;12;8M", None),
        ):
            remaining = bytearray(sequence)

            def read(_fd, _count):
                return bytes([remaining.pop(0)])

            def ready(*_args):
                return ([sys.stdin] if remaining else [], [], [])

            with self.subTest(sequence=sequence), patch.object(
                sys.stdin, "isatty", return_value=True
            ), patch.object(select, "select", side_effect=ready), patch.object(
                goodmon.os, "read", side_effect=read
            ):
                self.assertEqual(goodmon.wait_key(0.1), expected)

    def test_json_without_psutil_is_actionable(self):
        error = io.StringIO()
        with patch.object(goodmon, "load_psutil", return_value=None), patch.object(
            goodmon, "maybe_reexec_venv"
        ), redirect_stderr(error):
            self.assertEqual(goodmon.main(["--json"]), 2)
        self.assertIn("README.md", error.getvalue())

    def test_help_and_themes_do_not_load_psutil(self):
        with patch.object(
            goodmon, "load_psutil", side_effect=AssertionError
        ), redirect_stdout(io.StringIO()):
            self.assertEqual(goodmon.main(["help"]), 0)
            self.assertEqual(goodmon.main(["temas"]), 0)


if __name__ == "__main__":
    unittest.main()
