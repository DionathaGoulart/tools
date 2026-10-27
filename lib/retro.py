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

``Retro(skin="good")`` swaps in the Good brand skin — the helldivers2-api
style guide (logo pair ``#fbee23`` + ``#000000``, themes ``black``/``yellow``,
see ``.harness/styleguide-terminal.md`` §7). Tools that don't pass ``skin``
are untouched.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import unicodedata


def _forcar_utf8() -> None:
    """The UI draws in box-drawing/block glyphs (─ █ ► ●), none of which exist in
    the legacy Windows codepages. When stdout is a pipe on Windows, python picks
    the locale encoding (cp1252) and a plain print() dies with UnicodeEncodeError.
    Pin UTF-8 (errors="replace" as a last resort) so no tool can crash on output."""
    for fluxo in (sys.stdout, sys.stderr):
        if fluxo is None:
            continue
        atual = (getattr(fluxo, "encoding", None) or "").lower().replace("-", "")
        if atual == "utf8":
            continue
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass  # StringIO/detached stream: nothing to reconfigure


_forcar_utf8()


class TerminalParser(argparse.ArgumentParser):
    """Ajuda do argparse também respeita terminais menores que seus rótulos."""

    def print_help(self, file=None) -> None:
        if file is None or file is sys.stdout:
            Retro().texto(self.format_help().rstrip("\n"))
        else:
            super().print_help(file)

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

# Good brand skin (helldivers2-api .harness/styleguide.md §2): the logo pair,
# one theme per order. Each: (background, foreground, accent, success-text,
# error-text) — the -text tones are the ones that keep 4.5:1 on that background.
TEMAS_GOOD: dict[str, tuple[str, str, str, str, str]] = {
    "black": ("000000", "fbee23", "fbee23", "4ade80", "f87171"),
    "yellow": ("fbee23", "000000", "000000", "166534", "b91c1c"),
}
TEMA_GOOD_PADRAO = "black"
MUTED_GOOD = 60  # muted-text = 60% of base-content over base-100 (§2.4)
LINHA_GOOD = 30  # hairlines/leaders = base-300 at 30% (§6.3 row separator)

_ANSI = re.compile(r"\033\[[0-9;]*m")
_PARTES = re.compile(r"\033\[[0-9;]*m|\n|.")


def largura(texto: str) -> int:
    """Visible width of a string: ANSI-free, wide chars count as 2."""
    limpo = _ANSI.sub("", texto)
    total = 0
    for ch in limpo:
        if unicodedata.combining(ch):
            continue
        total += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return total


def cortar(texto: str, limite: int, sufixo: str = "…") -> str:
    """Corta por células de terminal sem quebrar ANSI, CJK ou acentos combinados."""
    if limite <= 0:
        return ""
    if largura(texto) <= limite:
        return texto
    reserva = largura(sufixo)
    usados = 0
    partes: list[str] = []
    for parte in _PARTES.findall(texto):
        if parte == "\n":
            break
        if _ANSI.fullmatch(parte):
            partes.append(parte)
            continue
        tamanho = largura(parte)
        if tamanho and usados + tamanho > max(0, limite - reserva):
            break
        partes.append(parte)
        usados += tamanho
    resultado = "".join(partes)
    if largura(sufixo) <= limite:
        resultado += sufixo
    return resultado + ("\033[0m" if "\033[" in resultado else "")


def quebrar(texto: str, limite: int) -> list[str]:
    """Quebra texto por células, preservando todos os caracteres e escapes ANSI."""
    if limite <= 0 or not texto:
        return [texto] if texto else [""]
    linhas: list[str] = []
    atual: list[str] = []
    usados = 0
    estilo = ""
    for parte in _PARTES.findall(texto):
        if parte == "\n":
            linhas.append("".join(atual) + ("\033[0m" if estilo else ""))
            atual, usados = [estilo] if estilo else [], 0
            continue
        if _ANSI.fullmatch(parte):
            atual.append(parte)
            estilo = "" if parte in ("\033[m", "\033[0m") else estilo + parte
            continue
        tamanho = largura(parte)
        if tamanho and usados and usados + tamanho > limite:
            linhas.append("".join(atual) + ("\033[0m" if estilo else ""))
            atual, usados = [estilo] if estilo else [], 0
        # A wide character cannot fit in a one-cell terminal. TTY output uses a
        # one-cell placeholder; pipes never call this branch and keep the data.
        if tamanho > limite:
            atual.append("?")
            usados += 1
            continue
        atual.append(parte)
        usados += tamanho
    linhas.append("".join(atual) + ("\033[0m" if estilo else ""))
    return linhas


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
        skin: str = "",
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
        self.good = skin == "good"
        if self.good:
            # RETRO_TEMA names a legacy palette for the other tools; anything
            # outside the brand pair falls back to black (§0.2).
            self.temas = {k: v[:3] for k, v in TEMAS_GOOD.items()}
            padrao = TEMA_GOOD_PADRAO
        else:
            self.temas = TEMAS
            padrao = TEMA_PADRAO
        self.tema = nome if nome in self.temas else padrao
        self.bg, self.fg_hex, self.acc = self.temas[self.tema]

        self.tty = sys.stdout.isatty()
        try:
            self._terminal_fd = sys.stdout.fileno() if self.tty else None
        except (AttributeError, OSError, ValueError):
            self._terminal_fd = None
        self.cor = self.tty and "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb"
        if self.cor and os.name == "nt":
            os.system("")  # legacy Windows console: turns on ANSI/VT processing
        colorterm = os.environ.get("COLORTERM", "")
        self.truecolor = self.cor and ("truecolor" in colorterm or "24bit" in colorterm)

        self.largura_caixa = max(1, largura_caixa)
        self.permitir_caixa = True
        self.cols = self.rows = self.bw = self.cf = 1
        self.caixa = False
        self.atualizar_tamanho()

        self._tokens()

    def atualizar_tamanho(self) -> tuple[int, int]:
        """Relê o terminal. Chame antes de redesenhos próprios de ferramentas."""
        try:
            tamanho = os.get_terminal_size(self._terminal_fd) if self._terminal_fd is not None else shutil.get_terminal_size((80, 24))
        except OSError:
            tamanho = shutil.get_terminal_size((80, 24))
        self.cols = max(1, tamanho.columns)
        self.rows = max(1, tamanho.lines)
        # Reserva uma coluna para a sombra quando houver caixa. Em telas menores,
        # o layout plano usa toda a largura e nunca força um mínimo artificial.
        self.bw = max(1, min(self.largura_caixa, self.cols - 1))
        self.cf = max(1, self.bw - 4)
        self.caixa = (
            self.permitir_caixa and self.tty
            and self.cols >= 46 and self.bw >= 20 and self.rows >= 12
        )
        return self.cols, self.rows

    def cortar(self, texto: str, largura_maxima: int | None = None) -> str:
        self.atualizar_tamanho()
        return cortar(texto, self.cols if largura_maxima is None else largura_maxima)

    def quebrar(self, texto: str, largura_maxima: int | None = None) -> list[str]:
        self.atualizar_tamanho()
        if not self.tty:
            return texto.split("\n")
        return quebrar(texto, self.cols if largura_maxima is None else largura_maxima)

    def texto(self, texto: str, largura_maxima: int | None = None) -> None:
        """Imprime prosa sem transbordar em TTY; pipes preservam a string inteira."""
        self.atualizar_tamanho()
        if not self.tty:
            print(texto)
            return
        limite = max(1, self.cols if largura_maxima is None else min(self.cols, largura_maxima))
        for linha in quebrar(texto, limite):
            print(linha)

    def _flat(self, texto: str) -> None:
        self.atualizar_tamanho()
        prefixo = "  " if self.cols >= 3 else ""
        if not self.tty:
            print(prefixo + texto)
            return
        for linha in quebrar(texto, max(1, self.cols - largura(prefixo))):
            print(prefixo + linha)

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
                "RESET BOLD DIM ITAL ACC ACC70 ACC50 ACC30 ACC15 FG FG70 FG40 INV OK ALERTA"
            ).split():
                setattr(self, nome, "")
            return

        self.RESET, self.BOLD, self.DIM = "\033[0m", "\033[1m", "\033[2m"
        self.ITAL = "\033[3m"
        if self.good:
            self._tokens_good()
        elif self.truecolor:
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

    def _tokens_good(self) -> None:
        """Good skin: two tones, no opacity ladder. Emphasis is the accent,
        dimming is muted-text (a colour, §2.4), hairlines are base-300/30."""
        if self.truecolor:
            _, _, _, ok, erro = TEMAS_GOOD[self.tema]
            muted = self._fg(mix(self.fg_hex, self.bg, MUTED_GOOD))
            linha = self._fg(mix(self.acc, self.bg, LINHA_GOOD))
            self.ACC = self._fg(self.acc)
            self.ACC70 = self.ACC50 = muted
            self.ACC30 = self.ACC15 = linha
            self.FG = self.FG70 = self._fg(self.fg_hex)
            self.FG40 = muted
            self.INV = self._bg(self.acc) + self._fg(self.bg)
            self.OK = self._fg(ok)
            self.ALERTA = self._fg(erro)
            return
        # 8 colours: yellow is the closest ANSI to #fbee23; the light theme's
        # ink is plain black on whatever background the terminal has.
        cor = "33" if self.tema == "black" else "30"
        self.ACC = f"\033[1;{cor}m"
        self.ACC70 = self.ACC50 = self.FG40 = f"\033[{cor}m"
        self.ACC30 = self.ACC15 = f"\033[2;{cor}m"
        self.FG = self.FG70 = f"\033[{cor}m"
        self.INV = f"\033[7;{cor}m"
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
        """``[ MODULE: X ]`` header — the module-card chrome of the style guide.
        Good skin: the screen-title (bold italic caps) + meta as bracketed
        machine micro-text (§3, §4.6)."""
        self.atualizar_tamanho()
        if self.good:
            linha = f"\n  {self.ACC}{self.BOLD}{self.ITAL}{rotulo.upper()}{self.RESET}"
            if meta:
                linha += (
                    f"  {self.ACC30}[{self.RESET}{self.FG40}{meta.upper()}"
                    f"{self.RESET}{self.ACC30}]{self.RESET}"
                )
            self.texto(linha)
            print()
            return
        linha = f"\n  {self.ACC}{self.BOLD}[ MODULE: {rotulo.upper()} ]{self.RESET}"
        if meta:
            linha += f"  {self.ACC30}{meta.upper()}{self.RESET}"
        self.texto(linha)
        print()

    def secao(self, rotulo: str) -> None:
        """``# HEADING`` sub-section label (good skin: the ``>`` kicker, §3)."""
        sigil = ">" if self.good else "#"
        self._flat(
            f"{self.ACC}{self.BOLD if self.good else ''}{sigil} {rotulo.upper()}{self.RESET}"
        )

    def _pontos(self) -> int:
        self.atualizar_tamanho()
        return max(1, min(44, self.cols - 4))

    def kv(self, chave: str, valor: str) -> None:
        """Key-value row with a dot leader: dim key · accent-bold value."""
        alvo = self._pontos()
        n = max(2, alvo - largura(chave) - largura(valor))
        self._flat(
            f"{self.FG40}{chave}{self.RESET} "
            f"{self.ACC15}{'·' * n}{self.RESET} "
            f"{self.ACC}{self.BOLD}{valor}{self.RESET}"
        )

    def regra(self) -> None:
        self._flat(f"{self.ACC15}{'─' * self._pontos()}{self.RESET}")

    def item(self, marca: str, texto: str, meta: str = "") -> None:
        """List row: accent marker, foreground text, dim trailing meta."""
        linha = f"{self.ACC}{marca}{self.RESET} {self.FG70}{texto}{self.RESET}"
        if meta:
            linha += f"  {self.FG40}{meta}{self.RESET}"
        self._flat(linha)

    def ok(self, texto: str) -> None:
        self._flat(
            f"{self.OK}[ OK ]{self.RESET} {self.ACC}{self.BOLD}{texto.upper()}{self.RESET}"
        )

    def erro(self, texto: str) -> None:
        self._flat(f"{self.ALERTA}[ ERRO ]{self.RESET} {texto}")

    def aviso(self, etiqueta: str, texto: str = "") -> None:
        self._flat(f"{self.FG40}[ {etiqueta.upper()} ]{self.RESET} {texto}")

    def proximo(self, comando: str, prefixo: str = "proximo passo:") -> None:
        self._flat(
            f"{self.ACC30}>{self.RESET} {prefixo}  {self.ACC}{self.BOLD}{comando}{self.RESET}"
        )

    def barra(self, feito: int, total: int, larg: int = 24) -> str:
        """ASCII progress bar: filled accent, rest accent/18, percentage.
        Good skin: solid track, no dithering (§4)."""
        self.atualizar_tamanho()
        total = max(1, total)
        larg = max(1, min(larg, max(1, self.cf - 7)))
        n = min(larg, feito * larg // total)
        pct = feito * 100 // total
        trilho = "█" if self.good else "▒"
        return (
            f"{self.ACC}{'█' * n}{self.ACC15}{trilho * (larg - n)}{self.RESET}"
            f"  {self.ACC}{self.BOLD}{pct:3d}%{self.RESET}"
        )

    # ---------- box (terminal window recipe) ----------
    @property
    def _sombra_col(self) -> str:
        """Right-hand shadow cell. Good skin: the hard offset shadow is the
        full --shadow colour, no blur, no dither (§4.1)."""
        if self.good:
            return f"{self.ACC}█{self.RESET}"
        return f"{self.ACC15}▒{self.RESET}"

    def topo(self) -> None:
        self.atualizar_tamanho()
        if not self.caixa:
            return
        print(f"{self.ACC}┏{'━' * (self.bw - 2)}┓{self.RESET}")

    def sep(self) -> None:
        self.atualizar_tamanho()
        if not self.caixa:
            return
        print(f"{self.ACC}┠{'─' * (self.bw - 2)}┨{self.RESET}{self._sombra_col}")

    def base(self) -> None:
        self.atualizar_tamanho()
        if not self.caixa:
            return
        print(f"{self.ACC}┗{'━' * (self.bw - 2)}┛{self.RESET}{self._sombra_col}")

    def sombra(self) -> None:
        self.atualizar_tamanho()
        if not self.caixa:
            return
        if self.good:
            print(f" {self.ACC}{'▀' * self.bw}{self.RESET}")
            return
        print(f" {self.ACC15}{'▒' * self.bw}{self.RESET}")

    def linha(self, conteudo: str = "") -> None:
        self.atualizar_tamanho()
        if not self.caixa:
            self._flat(conteudo)
            return
        for parte in quebrar(conteudo, self.cf):
            pad = max(0, self.cf - largura(parte))
            print(
                f"{self.ACC}┃{self.RESET} {parte}{' ' * pad} "
                f"{self.ACC}┃{self.RESET}{self._sombra_col}"
            )

    def chrome(self, titulo: str, meta: str = "") -> None:
        """Window chrome bar: three accent dots, path title, right-hand meta.
        Good skin: the window-bar — FILE.NAME in muted caps on the left, meta,
        then the three square WindowDots on the right (§4.7, §4.8)."""
        self.atualizar_tamanho()
        if not self.caixa:
            self._flat(f"{titulo} {meta}".strip())
            return
        if self.good:
            dots = f"{self.ACC}■ ■ ■{self.RESET}"
            meta = cortar(meta, max(1, self.cf // 3))
            nome = cortar(titulo.upper(), max(1, self.cf - 10 - largura(meta)))
            pad = max(1, self.cf - 7 - largura(nome) - largura(meta))
            print(
                f"{self.ACC}┃{self.RESET} {self.FG40}{self.BOLD}{nome}{self.RESET}{' ' * pad}"
                f"{self.FG40}{meta}{self.RESET}  {dots} {self.ACC}┃{self.RESET}{self._sombra_col}"
            )
            return
        meta = cortar(meta, max(1, self.cf // 3))
        titulo = cortar(titulo, max(1, self.cf - 8 - largura(meta)))
        pad = max(1, self.cf - 7 - largura(titulo) - largura(meta))
        print(
            f"{self.ACC}┃{self.RESET} {self.ACC}●{self.RESET} {self.ACC50}●{self.RESET} "
            f"{self.ACC30}●{self.RESET}  {self.ACC50}{titulo}{self.RESET}{' ' * pad}"
            f"{self.ACC30}{meta}{self.RESET} {self.ACC}┃{self.RESET}{self._sombra_col}"
        )

    def status(self, esquerda: str, direita: str = "") -> None:
        """Inverted status bar at the bottom of a window."""
        self.atualizar_tamanho()
        if not self.caixa:
            self._flat(f"{esquerda} {direita}".strip())
            return
        direita = cortar(direita, max(1, self.cf // 3))
        esquerda = cortar(esquerda, max(1, self.cf - largura(direita) - 1))
        pad = max(1, self.cf - largura(esquerda) - largura(direita))
        print(
            f"{self.ACC}┃{self.INV}{self.BOLD} {esquerda}{' ' * pad}{direita} {self.RESET}"
            f"{self.ACC}┃{self.RESET}{self._sombra_col}"
        )

    def janela(
        self, titulo: str, linhas: list[str], meta: str = "", rodape: str = ""
    ) -> None:
        """Full terminal window: chrome + body + optional status bar + shadow."""
        self.atualizar_tamanho()
        if not self.caixa:
            for ln in linhas:
                self._flat(ln)
            return
        self.topo()
        self.chrome(titulo, meta)
        self.sep()
        for ln in linhas:
            self.linha(ln)
        if rodape:
            self.sep()
            self.status(rodape)
        self.base()
        self.sombra()

    # ---------- theme catalog ----------
    def catalogo_temas(self) -> None:
        self.atualizar_tamanho()
        self.modulo("theme_catalog")
        for nome, (hb, hf, ha) in self.temas.items():
            marca = "► " if nome == self.tema else "  "
            if self.truecolor:
                swatch = (
                    f"{self._bg(ha)}    {self.RESET}{self._bg(hf)}  {self.RESET}"
                    f"{self._bg(hb)}  {self.RESET}"
                )
            else:
                swatch = f"[#{ha}]"
            self._flat(
                f"{self.ACC}{marca}{self.RESET}{nome:<16} {swatch}  "
                f"{self.ACC15}#{ha}{self.RESET}"
            )
        self._flat(f"export {self.env_var}=<nome>{self.RESET}")
