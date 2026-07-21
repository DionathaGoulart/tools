"""llm.py — shared OpenRouter client for the python tools in this repo.

Every AI tool used to carry its own copy of the OpenRouter transport (key
lookup, model fallback loop, timeout, 401 handling, JSON extraction). This
centralises all of that so a fix or improvement lands in one place.

Usage from a tool that lives in ``tools/<name>/<name>``::

    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "lib"))
    from llm import LLM, LLMError

    llm = LLM("goodvocab", DEFAULT_MODELS)
    try:
        content, model = llm.chat(messages, max_tokens=3000, temperature=0.8)
    except LLMError as e:
        die(...)   # each tool keeps its own error copy / presentation

``chat`` never prints or exits: it raises :class:`LLMError` with a ``kind``
(``no_key`` | ``auth`` | ``all_failed`` | ``fetch``) so the caller decides how
to present the failure. Only the standard library is used — the tools stay
dependency-free and portable.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_URL = "https://openrouter.ai/api/v1/models"
# sent to OpenRouter for attribution; shared by every tool in this repo
REFERER = "https://github.com/DionathaGoulart/tools"


class LLMError(Exception):
    """Transport failure. ``kind`` lets the caller pick the right message.

    kind:
      - ``no_key``     — OPENROUTER_API_KEY missing from the environment
      - ``auth``       — key present but rejected (HTTP 401)
      - ``all_failed`` — every configured model failed (see ``errors``)
      - ``fetch``      — the /models listing request failed
    """

    def __init__(self, message: str, *, kind: str = "all_failed", errors=()):
        super().__init__(message)
        self.message = message
        self.kind = kind
        self.errors = list(errors)


def extrair_json(texto: str, tipo: str = "array"):
    """Pull the JSON out of a model reply (tolerates markdown fences, reasoning
    and surrounding prose). Returns the parsed value, or ``None`` if no JSON of
    the requested ``tipo`` ("array" | "objeto") is found."""
    abre = "[" if tipo == "array" else "{"
    texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL).strip()
    dec = json.JSONDecoder()
    i = texto.find(abre)
    while i != -1:
        try:
            valor, _ = dec.raw_decode(texto, i)
            # commands expect an array of objects or a single object — avoid
            # grabbing stray brackets from the surrounding text (e.g. "lista[0]")
            if tipo == "array":
                if isinstance(valor, list) and valor and all(isinstance(x, dict) for x in valor):
                    return valor
            elif isinstance(valor, dict) and valor:
                return valor
        except json.JSONDecodeError:
            pass
        i = texto.find(abre, i + 1)
    return None


class LLM:
    """Minimal OpenRouter chat client with per-model fallback.

    ``title`` is sent as the ``X-Title`` header (the tool's name).
    ``default_models`` is tried in order when ``OPENROUTER_MODEL`` is unset.
    """

    def __init__(self, title: str, default_models, *, referer: str = REFERER, timeout: int = 180):
        self.title = title
        self.default_models = list(default_models)
        self.referer = referer
        self.timeout = timeout

    def modelos(self):
        """The model list to try: ``OPENROUTER_MODEL`` (comma-separated) or the
        tool's defaults."""
        env = os.environ.get("OPENROUTER_MODEL", "").strip()
        if env:
            return [m.strip() for m in env.split(",") if m.strip()]
        return list(self.default_models)

    def _key(self) -> str:
        key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not key:
            raise LLMError("OPENROUTER_API_KEY não definida", kind="no_key")
        return key

    def chat(self, messages, *, max_tokens: int = 3000, temperature: float = 0.8, json_tipo=None):
        """Try each configured model in order, returning ``(conteudo, modelo)``.

        With ``json_tipo`` ("array" | "objeto") the reply is parsed and validated
        as JSON before being accepted — a model that returns broken JSON counts
        as a failure and falls through to the next. ``conteudo`` is the parsed
        value when ``json_tipo`` is given, otherwise the raw string.

        Raises :class:`LLMError` (``no_key`` / ``auth`` / ``all_failed``).
        """
        key = self._key()
        erros = []
        for model in self.modelos():
            payload = json.dumps({
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }).encode("utf-8")
            req = urllib.request.Request(
                API_URL,
                data=payload,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.referer,
                    "X-Title": self.title,
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                content = (data["choices"][0]["message"].get("content") or "").strip()
                if not content:
                    erros.append(f"{model}: resposta vazia")
                    continue
                if json_tipo is None:
                    return content, model
                parsed = extrair_json(content, json_tipo)
                if parsed is not None:
                    return parsed, model
                erros.append(f"{model}: não devolveu JSON parseável")
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    raise LLMError("OPENROUTER_API_KEY inválida (HTTP 401).", kind="auth")
                erros.append(f"{model}: HTTP {e.code}")
            except Exception as e:  # rede, timeout, JSON…
                erros.append(f"{model}: {type(e).__name__}: {e}")
        raise LLMError("todos os modelos falharam", kind="all_failed", errors=erros)

    def free_models(self):
        """Sorted list of the OpenRouter model ids ending in ``:free``.

        Raises :class:`LLMError` (``fetch``) if the listing request fails."""
        try:
            with urllib.request.urlopen(MODELS_URL, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            raise LLMError(f"não consegui consultar {MODELS_URL}: {e}", kind="fetch")
        return sorted(m["id"] for m in data.get("data", []) if m["id"].endswith(":free"))
