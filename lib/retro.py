"""retro.py — shared retro-terminal theme for the python tools in this repo.

Usage from a tool that lives in ``tools/<name>/<name>``::

    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "lib"))
    from retro import Retro

    ui = Retro(env_prefix="VOCAB")     # reads VOCAB_TEMA, then RETRO_TEMA
    ui.modulo("word_of_the_day", "src: openrouter")
    ui.kv("PALAVRA", "SERENDIPITY")

Implements ``.harness/styleguide-terminal.md``: accent-only palette, square
corners, heavy borders, flat offset shadow, uppercase labels, no gradients.
``NO_COLOR`` and non-tty output degrade to plain text.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import unicodedata

# each theme: (background, foreground, accent) — hex, no '#'
TEMAS: dict[str, tuple[str, str, str]] = {
    "vault-gold": ("111111", "e0e0e0", "c8a96e"),
    "noir-rose": ("121212", "f2efe7", "e8729a"),
    "midnight-ember": ("0d1117", "e0ffe0", "ff6b45"),
    "cyber-teal": ("0a0f14", "e0f4ff", "00e5ff"),
    "velvet-purple": ("0e0a14", "ede0ff", "b47aff"),
    "abyss-frost": ("e4f0f6", "0f172a", "0a0f1e"),
    "crimson-chalk": ("f2efe7", "1a0a0a", "dc143c"),
    "forest-mist": ("eef4ee", "1a2e1a", "2d6a2d"),
    "sand-dusk": ("f5f0e8", "2a1a0a", "b56a30"),
}
TEMA_PADRAO = "vault-gold"

_ANSI = re.compile(r"\033\[[0-9;]*m")


def largura(texto: str) -> int:
    """Visible width of a string: ANSI-free, wide chars count as 2."""
    limpo = _ANSI.sub("", texto)
    total = 0
    for ch in limpo:
        if unicodedata.combining(ch):
            continue
        total += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return total


def _rgb(hexa: str) -> tuple[int, int, int]:
    return int(hexa[0:2], 16), int(hexa[2:4], 16), int(hexa[4:6], 16)


def mix(a: str, b: str, alfa: int) -> str:
    """Blend hex ``a`` over hex ``b`` at ``alfa``% — the style guide's opacity steps."""
    ar, ag, ab = _rgb(a)
    br, bg, bb = _rgb(b)
    return "%02x%02x%02x" % (
        (ar * alfa + br * (100 - alfa)) // 100,
        (ag * alfa + bg * (100 - alfa)) // 100,
        (ab * alfa + bb * (100 - alfa)) // 100,
    )


class Retro:
    """Style-guide tokens + component recipes for a terminal UI."""

    def __init__(
        self,
        env_prefix: str = "",
        tema: str | None = None,
        largura_caixa: int = 52,
        env_var: str | None = None,
    ):
        # env_var overrides the default <PREFIX>_TEMA name — use it when the tool
        # already owns that variable for something else (vocab: VOCAB_PALETA).
        self.env_var = env_var or (f"{env_prefix}_TEMA" if env_prefix else "RETRO_TEMA")
        nome = (
            tema
            or os.environ.get(self.env_var)
            or os.environ.get("RETRO_TEMA")
            or TEMA_PADRAO
        )
        self.tema = nome if nome in TEMAS else TEMA_PADRAO
        self.bg, self.fg_hex, self.acc = TEMAS[self.tema]

        self.tty = sys.stdout.isatty()
        self.cor = self.tty and not os.environ.get("NO_COLOR")
        if self.cor and os.name == "nt":
            os.system("")  # legacy Windows console: turns on ANSI/VT processing
        colorterm = os.environ.get("COLORTERM", "")
        self.truecolor = self.cor and ("truecolor" in colorterm or "24bit" in colorterm)

        self.cols = shutil.get_terminal_size((80, 24)).columns
        self.bw = min(largura_caixa, max(20, self.cols - 3))
        self.caixa = self.tty and self.bw >= 46
        self.cf = self.bw - 4

        self._tokens()

    # ---------- tokens ----------
    def _fg(self, hexa: str) -> str:
        r, g, b = _rgb(hexa)
        return f"\033[38;2;{r};{g};{b}m"

    def _bg(self, hexa: str) -> str:
        r, g, b = _rgb(hexa)
        return f"\033[48;2;{r};{g};{b}m"

    def _tokens(self) -> None:
        if not self.cor:
            for nome in (
                "RESET BOLD DIM ACC ACC70 ACC50 ACC30 ACC15 FG FG70 FG40 INV OK ALERTA"
            ).split():
                setattr(self, nome, "")
            return

        self.RESET, self.BOLD, self.DIM = "\033[0m", "\033[1m", "\033[2m"
        if self.truecolor:
            self.ACC = self._fg(self.acc)
            self.ACC70 = self._fg(mix(self.acc, self.bg, 70))
            self.ACC50 = self._fg(mix(self.acc, self.bg, 50))
            self.ACC30 = self._fg(mix(self.acc, self.bg, 30))
            self.ACC15 = self._fg(mix(self.acc, self.bg, 18))
            self.FG = self._fg(self.fg_hex)
            self.FG70 = self._fg(mix(self.fg_hex, self.bg, 70))
            self.FG40 = self._fg(mix(self.fg_hex, self.bg, 40))
            self.INV = self._bg(self.acc) + self._fg(self.bg)
            self.OK = self._fg("3fb950")
            self.ALERTA = self._fg("e5534b")
        else:
            self.ACC = "\033[1;33m"
            self.ACC70 = self.ACC50 = "\033[33m"
            self.ACC30 = self.ACC15 = "\033[2;33m"
            self.FG = self.FG70 = "\033[0m"
            self.FG40 = "\033[2m"
            self.INV = "\033[7;33m"
            self.OK = "\033[1;32m"
            self.ALERTA = "\033[1;31m"

    # ---------- inline helpers ----------
    def acento(self, texto: str) -> str:
        return f"{self.ACC}{texto}{self.RESET}"

    def forte(self, texto: str) -> str:
        return f"{self.ACC}{self.BOLD}{texto}{self.RESET}"

    def apagado(self, texto: str) -> str:
        return f"{self.FG40}{texto}{self.RESET}"

    def chip(self, texto: str) -> str:
        """Tech tag / status chip: bracketed, uppercase, accent."""
        return f"{self.ACC30}[{self.RESET}{self.ACC}{texto.upper()}{self.RESET}{self.ACC30}]{self.RESET}"

    def invertido(self, texto: str) -> str:
        return f"{self.INV}{self.BOLD} {texto.upper()} {self.RESET}"

    # ---------- flat blocks ----------
    def modulo(self, rotulo: str, meta: str = "") -> None:
        """``[ MODULE: X ]`` header — the module-card chrome of the style guide."""
        linha = f"\n  {self.ACC}{self.BOLD}[ MODULE: {rotulo.upper()} ]{self.RESET}"
        if meta:
            linha += f"  {self.ACC30}{meta.upper()}{self.RESET}"
        print(linha + "\n")

    def secao(self, rotulo: str) -> None:
        """``# HEADING`` sub-section label."""
        print(f"  {self.ACC}# {rotulo.upper()}{self.RESET}")

    def _pontos(self) -> int:
        return max(20, 44 if self.cols > 60 else self.cols - 12)

    def kv(self, chave: str, valor: str) -> None:
        """Key-value row with a dot leader: dim key · accent-bold value."""
        alvo = self._pontos()
        n = max(2, alvo - largura(chave) - largura(valor))
        print(
            f"  {self.FG40}{chave}{self.RESET} "
            f"{self.ACC15}{'·' * n}{self.RESET} "
            f"{self.ACC}{self.BOLD}{valor}{self.RESET}"
        )

    def regra(self) -> None:
        print(f"  {self.ACC15}{'─' * self._pontos()}{self.RESET}")

    def item(self, marca: str, texto: str, meta: str = "") -> None:
        """List row: accent marker, foreground text, dim trailing meta."""
        linha = f"  {self.ACC}{marca}{self.RESET} {self.FG70}{texto}{self.RESET}"
        if meta:
            linha += f"  {self.FG40}{meta}{self.RESET}"
        print(linha)

    def ok(self, texto: str) -> None:
        print(f"  {self.OK}[ OK ]{self.RESET} {self.ACC}{self.BOLD}{texto.upper()}{self.RESET}")

    def erro(self, texto: str) -> None:
        print(f"  {self.ALERTA}[ ERRO ]{self.RESET} {texto}")

    def aviso(self, etiqueta: str, texto: str = "") -> None:
        print(f"  {self.FG40}[ {etiqueta.upper()} ]{self.RESET} {texto}")

    def proximo(self, comando: str, prefixo: str = "proximo passo:") -> None:
        print(f"  {self.ACC30}>{self.RESET} {prefixo}  {self.ACC}{self.BOLD}{comando}{self.RESET}")

    def barra(self, feito: int, total: int, larg: int = 24) -> str:
        """ASCII progress bar: filled accent, rest accent/18, percentage."""
        total = max(1, total)
        n = min(larg, feito * larg // total)
        pct = feito * 100 // total
        return (
            f"{self.ACC}{'█' * n}{self.ACC15}{'▒' * (larg - n)}{self.RESET}"
            f"  {self.ACC}{self.BOLD}{pct:3d}%{self.RESET}"
        )

    # ---------- box (terminal window recipe) ----------
    def topo(self) -> None:
        print(f"{self.ACC}┏{'━' * (self.bw - 2)}┓{self.RESET}")

    def sep(self) -> None:
        print(f"{self.ACC}┠{'─' * (self.bw - 2)}┨{self.RESET}{self.ACC15}▒{self.RESET}")

    def base(self) -> None:
        print(f"{self.ACC}┗{'━' * (self.bw - 2)}┛{self.RESET}{self.ACC15}▒{self.RESET}")

    def sombra(self) -> None:
        print(f" {self.ACC15}{'▒' * self.bw}{self.RESET}")

    def linha(self, conteudo: str = "") -> None:
        pad = max(0, self.cf - largura(conteudo))
        print(
            f"{self.ACC}┃{self.RESET} {conteudo}{' ' * pad} "
            f"{self.ACC}┃{self.RESET}{self.ACC15}▒{self.RESET}"
        )

    def chrome(self, titulo: str, meta: str = "") -> None:
        """Window chrome bar: three accent dots, path title, right-hand meta."""
        pad = max(1, self.cf - 7 - largura(titulo) - largura(meta))
        print(
            f"{self.ACC}┃{self.RESET} {self.ACC}●{self.RESET} {self.ACC50}●{self.RESET} "
            f"{self.ACC30}●{self.RESET}  {self.ACC50}{titulo}{self.RESET}{' ' * pad}"
            f"{self.ACC30}{meta}{self.RESET} {self.ACC}┃{self.RESET}{self.ACC15}▒{self.RESET}"
        )

    def status(self, esquerda: str, direita: str = "") -> None:
        """Inverted status bar at the bottom of a window."""
        pad = max(1, self.cf - largura(esquerda) - largura(direita))
        print(
            f"{self.ACC}┃{self.INV}{self.BOLD} {esquerda}{' ' * pad}{direita} {self.RESET}"
            f"{self.ACC}┃{self.RESET}{self.ACC15}▒{self.RESET}"
        )

    def janela(self, titulo: str, linhas: list[str], meta: str = "", rodape: str = "") -> None:
        """Full terminal window: chrome + body + optional status bar + shadow."""
        if not self.caixa:
            for l in linhas:
                print(f"  {l}")
            return
        self.topo()
        self.chrome(titulo, meta)
        self.sep()
        for l in linhas:
            self.linha(l)
        if rodape:
            self.sep()
            self.status(rodape)
        self.base()
        self.sombra()

    # ---------- theme catalog ----------
    def catalogo_temas(self) -> None:
        self.modulo("theme_catalog")
        for nome, (hb, hf, ha) in TEMAS.items():
            marca = "► " if nome == self.tema else "  "
            if self.truecolor:
                swatch = (
                    f"{self._bg(ha)}    {self.RESET}{self._bg(hf)}  {self.RESET}"
                    f"{self._bg(hb)}  {self.RESET}"
                )
            else:
                swatch = f"[#{ha}]"
            print(
                f"  {self.ACC}{marca}{self.RESET}{nome:<16} {swatch}  "
                f"{self.ACC15}#{ha}{self.RESET}"
            )
        print(f"\n  {self.FG40}export {self.env_var}=<nome>{self.RESET}\n")
