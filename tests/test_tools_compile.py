"""Guard test: every python tool and shared lib must byte-compile.

Cheap regression net for the single-file tools — catches syntax breakage from
a refactor before it ships. Run from the repo root:

    python3 -m unittest discover -s tests
"""

import os
import py_compile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

PY_TOOLS = [
    "lib/llm.py",
    "lib/retro.py",
    "lib/imgcore.py",
    "dark/dark",
    "goodivers/goodivers",
    "goodjob/goodjob",
    "goodvocab/goodvocab",
    "goodprof/goodprof",
    "goodbio/goodbio",
    "goodzap/goodzap",
    "goodhunter/goodhunter",
    "images/goodpixel/goodpixel",
    "images/goodprofile/goodprofile",
]


class TestToolsCompile(unittest.TestCase):
    def test_todos_compilam(self):
        for rel in PY_TOOLS:
            caminho = os.path.join(ROOT, rel)
            with self.subTest(tool=rel):
                self.assertTrue(os.path.exists(caminho), f"sumiu: {rel}")
                py_compile.compile(caminho, doraise=True)


if __name__ == "__main__":
    unittest.main()
