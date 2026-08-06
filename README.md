# ai-coder-kimi

**Fork von [ai-coder](https://github.com/derleiti/ai-coder), fest auf [Kimi K3](https://platform.kimi.ai/docs/guide/kimi-k3-quickstart) (Moonshot AI) verdrahtet.**

Terminalbasierter Coding & DevOps Agent für AILinux / TriForce.

**Prinzip:** Dünner lokaler CLI-Client — Intelligenz sitzt im Backend. Anders
als das Original wählt dieser Fork das Modell nicht mehr frei aus 625+
Backend-Modellen, sondern verdrahtet Operator- und Fallback-Modell fest auf
Kimi K3.

## Was ist anders als im Original?

| | ai-coder (Original) | ai-coder-kimi (dieser Fork) |
|---|---|---|
| Modellwahl | Interaktiver Picker, 625+ Modelle | Fest auf Kimi K3, auto-erkannt aus dem Backend-Katalog |
| Fallback | frei wählbar (Default: `ollama/llama3.2:latest`) | kein Fremd-Modell mehr (Default: leer) |
| Config-Verzeichnis | `~/.config/ai-coder/` | `~/.config/ai-coder-kimi/` (kollidiert nicht mit dem Original) |
| CLI-Befehl | `aicoder` | `aicoder-kimi` |
| Transport | TriForce-Backend (`api.ailinux.me`) | unverändert — TriForce-Backend |

Login, Auth, MCP-Tools, Swarm-Mechanik, GUI und alle Befehle sind
unverändert aus dem Original übernommen. Geändert wurde ausschließlich,
**welches Modell** angefragt wird — siehe [`aicoder/kimi.py`](aicoder/kimi.py).

## Wie die Kimi-K3-Bindung funktioniert

Das TriForce-Backend routet Modelle unter unterschiedlichen Provider-Präfixen
(z.B. `groq/moonshotai/kimi-k2-instruct` für K2 via Groq). Welches Präfix für
Kimi K3 gilt, hängt vom Live-Katalog des Backends ab. Deshalb sucht der
Setup-Wizard beim ersten Start `/v1/client/models` nach einem Eintrag, der
`kimi-k3` enthält, und übernimmt genau diese ID automatisch — kein manuelles
Rätselraten nötig.

Falls das Backend K3 (noch) nicht listet, wird ersatzweise nach `kimi-k2`
gesucht; schlägt auch das fehl, greift ein statischer Default
(`moonshotai/kimi-k3`). Override jederzeit möglich:

```bash
aicoder-kimi model <exakte-id>          # dauerhaft in state.json
AICODER_KIMI_MODEL=<exakte-id> aicoder-kimi   # einmalig per Env-Var
```

### Offizielle Kimi-K3-Referenz (Moonshot AI, Stand 2026-08)

- Direkte Herstellerdoku: <https://platform.kimi.ai/docs/guide/kimi-k3-quickstart>
- API-Referenz: <https://platform.kimi.ai/docs/api/chat>
- Direkter Endpoint (falls jemand ohne TriForce direkt gegen Moonshot bauen will):
  `POST https://api.moonshot.ai/v1/chat/completions`, `Authorization: Bearer $MOONSHOT_API_KEY`,
  OpenAI-kompatibles Schema, Modell-ID `kimi-k3`, 1M Token Kontext,
  `reasoning_effort` (`low`/`high`/`max`, Default `max`).

## Installation

```bash
git clone <dieses-repo> ai-coder-kimi
cd ai-coder-kimi
pip install -e .
aicoder-kimi            # Setup-Wizard (Login) + Agent-REPL, Modell auto-erkannt
```

Koexistenz mit dem Original ist bewusst möglich: eigener Config-Ordner
(`~/.config/ai-coder-kimi/`), eigener Befehlsname (`aicoder-kimi`), eigener
User-Agent-String gegenüber dem Backend.

## Schnellstart

```bash
aicoder-kimi                   # Setup-Wizard (nur Login) + Agent-REPL
aicoder-kimi login             # Login gegen TriForce Backend
aicoder-kimi status            # model, fallback, swarm, workspace
aicoder-kimi ask "Was macht diese Funktion?"
aicoder-kimi task "Add docstrings" -f datei.py --dry-run
```

## Commands

Identisch zum Original — siehe [Original-README](https://github.com/derleiti/ai-coder#commands).
`model`/`fallback` funktionieren weiterhin manuell, sind aber standardmäßig
auf Kimi K3 vorbelegt statt leer.

## Architektur

Siehe `docs/architecture.md` (unverändert vom Original) sowie
`aicoder/kimi.py` für die K3-spezifische Ergänzung.

## Lizenz

Wie das Original: MIT License. Fork erstellt am 2026-08-06.
Original Copyright (c) 2026 Markus Leitermann / AILinuX <support@ailinux.me>.
Siehe [LICENSE](./LICENSE).
