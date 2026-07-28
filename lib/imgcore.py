"""imgcore.py — shared image decode/encode for the image tools in this repo.

Decodes with whatever backend is available (Pillow first, then the ImageMagick
CLI) and hands the tool a raw 8-bit buffer; writes PNG back out in pure
python. The tools transform the pixels themselves, so the output is identical
no matter which backend decoded the file — the only thing that can be missing
is the *decoder*. No pip install for the tools themselves.

Usage from a tool that lives in ``tools/images/<name>/<name>``::

    sys.path.insert(0, os.path.join(..., "..", "..", "lib"))
    import imgcore

    w, h, buf = imgcore.decode(path, 2048)              # RGB, 3 bytes/px
    w, h, buf = imgcore.decode(path, 2048, alpha=True)  # RGBA, 4 bytes/px
    imgcore.write_png(dst, w, h, buf, alpha=True)
"""

from __future__ import annotations

import struct
import subprocess
import zlib
from pathlib import Path
from shutil import which

RASTER = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".ppm"}
VECTOR = {".svg", ".pdf", ".eps", ".ai"}


# ---------------------------------------------------------------- decoding
def _decode_pillow(path: Path, maxdim: int, alpha: bool):
    from PIL import Image  # type: ignore

    im = Image.open(path)
    modo = "RGBA" if alpha else "RGB"
    if im.mode != modo:
        im = im.convert(modo)
    if max(im.size) > maxdim:
        im.thumbnail((maxdim, maxdim), Image.LANCZOS)
    return im.width, im.height, im.tobytes()


def _decode_magick(path: Path, maxdim: int, vector: bool, alpha: bool):
    magick = which("magick") or which("convert")
    if not magick:
        return None
    cmd = [magick]
    if vector:
        # render vectors big, then let the resize step shrink cleanly
        cmd += ["-background", "none", "-density", "384"]
    cmd += [str(path), "-resize", f"{maxdim}x{maxdim}>", "-depth", "8"]
    if alpha:
        cmd += ["-alpha", "set", "pam:-"]
    else:
        cmd += ["ppm:-"]
    out = subprocess.run(cmd, capture_output=True)
    if out.returncode != 0 or not out.stdout:
        return None
    return parse_pam(out.stdout) if alpha else parse_ppm(out.stdout)


def parse_ppm(data: bytes):
    """Minimal P6 binary PPM reader (magic, w, h, maxval, then RGB bytes)."""
    if data[:2] != b"P6":
        raise ValueError("saída do decoder não é PPM P6")
    tokens: list[bytes] = []
    i = 2
    n = len(data)
    while len(tokens) < 3 and i < n:
        while i < n and data[i] in b" \t\n\r":
            i += 1
        if i < n and data[i:i + 1] == b"#":  # comment line
            while i < n and data[i] not in b"\n\r":
                i += 1
            continue
        start = i
        while i < n and data[i] not in b" \t\n\r":
            i += 1
        tokens.append(data[start:i])
    w, h, maxv = (int(t) for t in tokens)
    i += 1  # single whitespace after maxval
    pixels = data[i:i + w * h * 3]
    if maxv != 255:  # rescale 16-bit-ish sources down to 8-bit
        pixels = bytes(v * 255 // maxv for v in pixels)
    return w, h, pixels


def parse_pam(data: bytes):
    """Minimal P7 PAM reader; expands GRAYSCALE/RGB tuple types to RGBA."""
    if data[:2] != b"P7":
        raise ValueError("saída do decoder não é PAM P7")
    fim = data.index(b"ENDHDR")
    campos: dict[str, str] = {}
    for linha in data[2:fim].decode("ascii", "replace").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        chave, _, valor = linha.partition(" ")
        campos[chave] = valor.strip()
    w = int(campos["WIDTH"])
    h = int(campos["HEIGHT"])
    depth = int(campos["DEPTH"])
    maxv = int(campos.get("MAXVAL", "255"))
    i = data.index(b"\n", fim) + 1
    pixels = data[i:i + w * h * depth]
    if maxv != 255:
        pixels = bytes(v * 255 // maxv for v in pixels)
    if depth == 4:
        return w, h, pixels
    out = bytearray(w * h * 4)
    o = 0
    if depth == 3:  # RGB
        for p in range(0, len(pixels), 3):
            out[o:o + 3] = pixels[p:p + 3]
            out[o + 3] = 255
            o += 4
    elif depth == 2:  # GRAYSCALE_ALPHA
        for p in range(0, len(pixels), 2):
            out[o] = out[o + 1] = out[o + 2] = pixels[p]
            out[o + 3] = pixels[p + 1]
            o += 4
    elif depth == 1:  # GRAYSCALE
        for v in pixels:
            out[o] = out[o + 1] = out[o + 2] = v
            out[o + 3] = 255
            o += 4
    else:
        raise ValueError(f"PAM com DEPTH {depth} não suportado")
    return w, h, bytes(out)


def decode(path: Path, maxdim: int, alpha: bool = False):
    """(w, h, buffer) — RGB (3 B/px), or RGBA (4 B/px) with ``alpha=True``."""
    ext = path.suffix.lower()
    vector = ext in VECTOR
    if not vector:
        try:
            return _decode_pillow(path, maxdim, alpha)
        except ImportError:
            pass
        except Exception:
            pass  # Pillow choked on the format — fall through to magick
    res = _decode_magick(path, maxdim, vector, alpha)
    if res is None:
        raise RuntimeError(
            "não consegui decodificar. Instale Pillow (pip install Pillow) "
            "ou ImageMagick (brew/apt/choco install imagemagick)."
        )
    return res


# ------------------------------------------------------------- PNG output
def _chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(path: Path, w: int, h: int, buf, alpha: bool = False) -> None:
    """8-bit truecolour PNG (RGB, or RGBA with ``alpha=True``), filter 0."""
    bpp = 4 if alpha else 3
    stride = w * bpp
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter type 0 (none)
        raw += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6 if alpha else 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(png)


# ------------------------------------------------------------- terminal preview
def preview(ui, w: int, h: int, buf, alpha: bool = False,
            maxw: int = 44, maxh: int = 32) -> None:
    """Half-block preview of a raw buffer (24-bit terminals only).

    RGBA buffers are composited over the theme background colour.
    """
    if not ui.truecolor:
        return
    bpp = 4 if alpha else 3
    fr, fg_, fb = (int(ui.bg[i:i + 2], 16) for i in (0, 2, 4))
    step = max(1, w // maxw, h // maxh)
    pw = w // step
    ph = h // step
    if pw < 2 or ph < 2:
        return

    def cor(px: int, py: int):
        i = (py * step * w + px * step) * bpp
        r, g, b = buf[i], buf[i + 1], buf[i + 2]
        if alpha:
            a = buf[i + 3]
            if a < 255:
                r = (r * a + fr * (255 - a)) // 255
                g = (g * a + fg_ * (255 - a)) // 255
                b = (b * a + fb * (255 - a)) // 255
        return r, g, b

    print()
    for py in range(0, ph - 1, 2):
        linha = "  "
        for px in range(pw):
            topo = cor(px, py)
            baixo = cor(px, min(py + 1, ph - 1))
            linha += (
                f"\033[38;2;{topo[0]};{topo[1]};{topo[2]}m"
                f"\033[48;2;{baixo[0]};{baixo[1]};{baixo[2]}m▀"
            )
        print(linha + ui.RESET)
    print()
