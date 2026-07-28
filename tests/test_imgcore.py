"""Tests for lib/imgcore.py — the pure parts (parsers + PNG writer).

Decoding via Pillow/ImageMagick is backend-dependent, so it stays out of CI;
everything here runs on the stdlib alone.
"""

import os
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import imgcore  # noqa: E402


def _ler_png(caminho):
    """Minimal PNG reader for filter-0 files written by imgcore.write_png."""
    data = Path(caminho).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos = 8
    ihdr = idat = b""
    while pos < len(data):
        tam = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        corpo = data[pos + 8:pos + 8 + tam]
        if tag == b"IHDR":
            ihdr = corpo
        elif tag == b"IDAT":
            idat += corpo
        pos += 12 + tam
    w, h, prof, tipo = struct.unpack(">IIBB", ihdr[:10])
    raw = zlib.decompress(idat)
    bpp = 4 if tipo == 6 else 3
    stride = w * bpp
    pixels = bytearray()
    for y in range(h):
        linha = raw[y * (stride + 1):(y + 1) * (stride + 1)]
        assert linha[0] == 0  # filter 0
        pixels += linha[1:]
    return w, h, prof, tipo, bytes(pixels)


class TestParsePPM(unittest.TestCase):
    def test_basico(self):
        data = b"P6\n2 1\n255\n" + bytes((255, 0, 0, 0, 0, 255))
        w, h, px = imgcore.parse_ppm(data)
        self.assertEqual((w, h), (2, 1))
        self.assertEqual(px, bytes((255, 0, 0, 0, 0, 255)))

    def test_comentario_e_maxval(self):
        data = b"P6\n# feito pelo magick\n1 1\n100\n" + bytes((100, 50, 0))
        w, h, px = imgcore.parse_ppm(data)
        self.assertEqual((w, h), (1, 1))
        self.assertEqual(px, bytes((255, 127, 0)))

    def test_magic_errado(self):
        with self.assertRaises(ValueError):
            imgcore.parse_ppm(b"P5\n1 1\n255\n\x00")


class TestParsePAM(unittest.TestCase):
    def _cabecalho(self, w, h, depth, tupltype):
        return (
            f"P7\nWIDTH {w}\nHEIGHT {h}\nDEPTH {depth}\nMAXVAL 255\n"
            f"TUPLTYPE {tupltype}\nENDHDR\n"
        ).encode()

    def test_rgba(self):
        data = self._cabecalho(1, 1, 4, "RGB_ALPHA") + bytes((1, 2, 3, 4))
        self.assertEqual(imgcore.parse_pam(data), (1, 1, bytes((1, 2, 3, 4))))

    def test_rgb_expande(self):
        data = self._cabecalho(2, 1, 3, "RGB") + bytes((1, 2, 3, 4, 5, 6))
        w, h, px = imgcore.parse_pam(data)
        self.assertEqual((w, h), (2, 1))
        self.assertEqual(px, bytes((1, 2, 3, 255, 4, 5, 6, 255)))

    def test_grayscale_expande(self):
        data = self._cabecalho(1, 1, 1, "GRAYSCALE") + bytes((9,))
        self.assertEqual(imgcore.parse_pam(data)[2], bytes((9, 9, 9, 255)))

    def test_grayscale_alpha_expande(self):
        data = self._cabecalho(1, 1, 2, "GRAYSCALE_ALPHA") + bytes((9, 40))
        self.assertEqual(imgcore.parse_pam(data)[2], bytes((9, 9, 9, 40)))

    def test_magic_errado(self):
        with self.assertRaises(ValueError):
            imgcore.parse_pam(b"P6\n1 1\n255\n\x00")


class TestWritePNG(unittest.TestCase):
    def _roundtrip(self, w, h, buf, alpha):
        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            imgcore.write_png(Path(tmp), w, h, buf, alpha=alpha)
            return _ler_png(tmp)
        finally:
            os.unlink(tmp)

    def test_rgb(self):
        buf = bytes((255, 0, 0, 0, 255, 0, 0, 0, 255, 10, 20, 30))
        w, h, prof, tipo, px = self._roundtrip(2, 2, buf, alpha=False)
        self.assertEqual((w, h, prof, tipo), (2, 2, 8, 2))
        self.assertEqual(px, buf)

    def test_rgba(self):
        buf = bytes((255, 0, 0, 128, 0, 255, 0, 0))
        w, h, prof, tipo, px = self._roundtrip(2, 1, buf, alpha=True)
        self.assertEqual((w, h, prof, tipo), (2, 1, 8, 6))
        self.assertEqual(px, buf)


if __name__ == "__main__":
    unittest.main()
