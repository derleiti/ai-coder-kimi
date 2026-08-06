from __future__ import annotations
"""
kimi.py — Kimi K3 model pinning für diesen Fork.

Dieser Fork von ai-coder ist darauf ausgelegt, ausschließlich mit Kimi K3
(Moonshot AI) zu arbeiten. Das TriForce-Backend (api.ailinux.me) bleibt als
Transport/Auth-Schicht bestehen — geändert wird nur, WELCHES Modell dort
angefragt wird.

Warum Auto-Detection statt eines einzelnen hartcodierten Strings?
TriForce routet Modelle unter unterschiedlichen Provider-Präfixen
(z.B. "groq/moonshotai/kimi-k2-instruct" für K2 via Groq). Welches Präfix
das Backend für Kimi K3 exakt verwendet, hängt vom Live-Modell-Katalog des
Backends ab (`/v1/client/models`). Deshalb wird beim Setup der Katalog
durchsucht und die beste Übereinstimmung für "kimi-k3" übernommen.

Quelle (Stand 2026-08, offizielle Doku):
  - https://platform.kimi.ai/docs/guide/kimi-k3-quickstart
  - https://platform.kimi.ai/docs/api/chat
  Direkte Moonshot-API: POST https://api.moonshot.ai/v1/chat/completions
  Modell-ID beim Hersteller: "kimi-k3" (1M Kontext, reasoning_effort
  low/high/max, OpenAI-kompatibles Chat-Completions-Schema).
"""

import os
from typing import Optional

# Override für Umgebungen, in denen der Katalog-Präfix bereits bekannt ist
# oder das Backend anders geroutet werden soll.
ENV_OVERRIDE = "AICODER_KIMI_MODEL"

# Bevorzugte Kandidaten in Prüfreihenfolge, falls der Live-Katalog nicht
# erreichbar ist (z.B. Erststart ohne Netzwerk). Deckt die bei diesem
# Backend bereits beobachtete Provider-Konvention (siehe Kimi K2 in
# setup.py: "groq/moonshotai/kimi-k2-instruct") sowie den nackten
# Hersteller-Modellnamen ab.
FALLBACK_CANDIDATES = [
    "moonshotai/kimi-k3",
    "groq/moonshotai/kimi-k3",
    "cerebras/moonshotai/kimi-k3",
    "openrouter/moonshotai/kimi-k3",
    "kimi-k3",
]

MATCH_TOKENS = ("kimi-k3", "kimi_k3", "kimik3")
LEGACY_MATCH_TOKENS = ("kimi-k2", "kimi_k2", "kimik2")


def _env_override() -> Optional[str]:
    val = os.environ.get(ENV_OVERRIDE, "").strip()
    return val or None


def detect_kimi_model(client=None) -> str:
    """Bestes verfügbares Kimi-K3-Modell im Backend-Katalog ermitteln.

    Reihenfolge:
      1. Expliziter Override via AICODER_KIMI_MODEL
      2. Live-Katalog (/v1/client/models) nach "kimi-k3" durchsuchen
      3. Live-Katalog nach "kimi-k2" durchsuchen (Backend hat K3 evtl. noch
         nicht gelistet — besser altes Kimi als ein Fremd-Modell)
      4. Statische Fallback-Kandidaten
    """
    override = _env_override()
    if override:
        return override

    if client is not None:
        try:
            models = client.list_models()
            ids = [
                (m.get("id") or m.get("model") or "")
                for m in models
                if isinstance(m, dict)
            ]
            for cand in ids:
                low = cand.lower()
                if any(tok in low for tok in MATCH_TOKENS):
                    return cand
            for cand in ids:
                low = cand.lower()
                if any(tok in low for tok in LEGACY_MATCH_TOKENS):
                    return cand
        except Exception:
            pass

    return FALLBACK_CANDIDATES[0]


def is_kimi_model(model_id: Optional[str]) -> bool:
    if not model_id:
        return False
    low = model_id.lower()
    return any(tok in low for tok in MATCH_TOKENS + LEGACY_MATCH_TOKENS)
