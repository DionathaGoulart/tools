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

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_URL = "https://openrouter.ai/api/v1/models"
# sent to OpenRouter for attribution; shared by every tool in this repo
REFERER = "https://github.com/DionathaGoulart/tools"
# bump when the cache record layout changes (invalidates old entries)
CACHE_VERSION = "v1"


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
        # ``finish_reason`` da última resposta aceita: "length" significa que o
        # modelo bateu ``max_tokens`` e a resposta veio cortada. Fica como
        # atributo (e não no retorno de ``chat``) pra não mexer na assinatura
        # que as outras ferramentas já usam. ``None`` num acerto de cache.
        self.last_finish_reason = None

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

    # --- response cache -----------------------------------------------------
    # Opt-in only: disabled unless a call passes ``cache_ttl`` or the env var
    # ``GOODTOOLS_LLM_CACHE_TTL`` is set. Keyed by the full request (title +
    # resolved model list + messages + params), so identical prompts within the
    # TTL are served from disk — saving :free quota and working offline.

    def _cache_root(self) -> str:
        root = os.environ.get("GOODTOOLS_CACHE_DIR", "").strip()
        if not root:
            root = os.path.join(os.path.expanduser("~"), ".cache", "goodtools", "llm")
        return root

    @staticmethod
    def _resolve_ttl(override) -> int:
        """Effective TTL in seconds: per-call ``override`` wins, else the env
        default, else 0 (disabled). Bad values fall back to 0."""
        raw = override if override is not None else os.environ.get("GOODTOOLS_LLM_CACHE_TTL", "")
        try:
            return max(0, int(raw)) if str(raw).strip() else 0
        except (TypeError, ValueError):
            return 0

    def _cache_key(self, messages, max_tokens, temperature, json_tipo) -> str:
        blob = json.dumps({
            "v": CACHE_VERSION,
            "title": self.title,
            "models": self.modelos(),
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "json_tipo": json_tipo,
        }, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def _cache_get(self, key: str, ttl: int):
        """Return ``(value, model)`` on a fresh hit, else ``None``. Never raises —
        a corrupt or unreadable entry is treated as a miss."""
        if ttl <= 0:  # cache disabled — never a hit (independent of the clock)
            return None
        path = os.path.join(self._cache_root(), key + ".json")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                rec = json.load(fh)
            if time.time() - float(rec["ts"]) > ttl:
                return None
            return rec["value"], rec["model"]
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def _cache_put(self, key: str, value, model: str) -> None:
        """Persist a successful reply. Best-effort — write failures are ignored."""
        try:
            root = self._cache_root()
            os.makedirs(root, exist_ok=True)
            path = os.path.join(root, key + ".json")
            tmp = f"{path}.{os.getpid()}.tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump({"ts": time.time(), "model": model, "value": value}, fh, ensure_ascii=False)
            os.replace(tmp, path)
        except OSError:
            pass

    def chat(self, messages, *, max_tokens: int = 3000, temperature: float = 0.8,
             json_tipo=None, cache_ttl=None):
        """Try each configured model in order, returning ``(conteudo, modelo)``.

        With ``json_tipo`` ("array" | "objeto") the reply is parsed and validated
        as JSON before being accepted — a model that returns broken JSON counts
        as a failure and falls through to the next. ``conteudo`` is the parsed
        value when ``json_tipo`` is given, otherwise the raw string.

        ``cache_ttl`` (seconds) opts this call into the on-disk response cache;
        when unset it falls back to the ``GOODTOOLS_LLM_CACHE_TTL`` env var, and
        to 0 (disabled) otherwise. A fresh hit is returned without any network
        call — no API key required — so repeated prompts are cheap and work
        offline. Only successful replies are cached.

        Raises :class:`LLMError` (``no_key`` / ``auth`` / ``all_failed``).
        """
        ttl = self._resolve_ttl(cache_ttl)
        self.last_finish_reason = None
        ckey = None
        if ttl > 0:
            ckey = self._cache_key(messages, max_tokens, temperature, json_tipo)
            hit = self._cache_get(ckey, ttl)
            if hit is not None:
                return hit  # (value, model), served from disk
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
                escolha = data["choices"][0]
                content = (escolha["message"].get("content") or "").strip()
                if not content:
                    erros.append(f"{model}: resposta vazia")
                    continue
                self.last_finish_reason = escolha.get("finish_reason")
                if json_tipo is None:
                    if ckey:
                        self._cache_put(ckey, content, model)
                    return content, model
                parsed = extrair_json(content, json_tipo)
                if parsed is not None:
                    if ckey:
                        self._cache_put(ckey, parsed, model)
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
