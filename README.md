# Tema 1 — Agent QA cu Tools + Prompts

Agent ReAct (Reasoning + Acting) cu **tool calling** validat prin Pydantic și **prompturi** încărcate din fișiere YAML. Funcționează cu orice backend compatibil OpenAI (LiteLLM, Anthropic, OpenAI, Ollama via LiteLLM).

**Curs:** AI Agent Development @ Skillab — Lecția 2.
**Autor:** Sandu Baboi.

---

## Arhitectură

```
tema_1/
├── prompts/                    # Prompturile sunt CONFIGURAȚIE, nu cod
│   ├── react_system.yaml       # System prompt cu placeholder-uri Jinja2
│   └── registry.py             # PromptRegistry (singleton lazy via @lru_cache)
│
├── tools/                      # 4 componente Tool Registry
│   ├── params_models.py        # Pydantic BaseModel per tool
│   ├── registry.py             # TOOL_REGISTRY + decorator @register_tool
│   ├── basic_tools.py          # calculator, datetime, web_search
│   └── tool_wrapper.py         # ToolWrapper.call() + catalog (OpenAI/Anthropic)
│
├── agent.py                    # Bucla ReAct + factory client LLM
├── test_prompts.py             # Verificare PromptRegistry
├── test_tools.py               # Verificare Tools (6 scenarii)
└── test_agent.py               # Verificare Agent (5 scenarii end-to-end)
```

---

## Pattern-uri implementate

| Pattern | Locație | Slide L2 |
|---|---|---|
| **Prompt Registry** | `prompts/registry.py` | S3 |
| **Decorator** (`@register_tool`) | `tools/registry.py` | S4.3 |
| **Factory** (`create_llm_client`) | `agent.py` | S4.4 |
| **Singleton lazy** (`@lru_cache`) | `prompts/registry.py` | S4.6 |
| **Tool Registry + Wrapper** | `tools/` | S7 |
| **ReAct loop** | `agent.py:react_loop` | S6 |

**Anti-patterns evitate:**
- `eval()` pentru calculator → folosit `ast.parse` cu whitelist operatori
- Loop infinit la tool calls → detecție repetiție identică + `max_iterations=10`
- Erori raw spre LLM → toate erorile capturate și transformate în mesaje human-readable

---

## Instalare

```bash
python -m venv venv
venv\Scripts\activate    # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

---

## Configurare provider LLM

Codul suportă **două** provideri prin variabilă de mediu — schimbi una, codul nu se atinge:

### Opțiunea A — Anthropic Claude (rapid, plătit)
```powershell
$env:LLM_PROVIDER = "anthropic"
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

### Opțiunea B — LiteLLM proxy (gratuit, orice model)
```powershell
$env:LLM_PROVIDER = "litellm"
# default: http://localhost:4000/v1, model "qwen"
# Recomand mistral sau modele >=7B pentru tool calling decent
```

---

## Rulare

### Mod interactiv (CLI chat)
```bash
python agent.py
```

### Mod programatic
```python
from agent import chat
answer = chat("Câte zile sunt din 24 mai până la 1 iunie 2026?")
print(answer)
```

### Testare
```bash
python test_prompts.py    # PromptRegistry — 3 verificări
python test_tools.py      # Tools cu Pydantic — 6 verificări
python test_agent.py      # Agent ReAct — 5 scenarii end-to-end
```

---

## Tool-uri disponibile

| Nume | Descriere | Validări Pydantic |
|---|---|---|
| `calculator` | Aritmetică sigură via `ast.parse` | `expression: str (min_length=1)` |
| `get_current_datetime` | Data/ora în fus orar IANA | `timezone: str (default='Europe/Bucharest')` |
| `web_search` | Mock — returnează rezultate placeholder | `query: str (min_length=2)`, `max_results: int (1-20)` |

Pentru adăugare tool nou: `tools/basic_tools.py` + decoratorul `@register_tool` → înregistrare automată.

---

## Concepte cheie

**Pydantic ca "single source of truth"** — definiția câmpului include tipul, validarea, descrierea pentru LLM, și (prin `.model_json_schema()`) JSON Schema-ul standard. Toate într-o singură declarație.

**ReAct loop** — fiecare iterație: LLM gândește → decide tool sau răspuns final → dacă tool: aplicația execută → rezultatul ajunge la LLM → urmează altă iterație. Bucla se oprește la `max_iterations` sau când LLM-ul răspunde direct fără tool calls.

**Provider-agnostic** — folosim OpenAI SDK pentru că majoritatea backend-urilor LLM oferă API OpenAI-compatible. Schimbi `base_url` + `api_key` + `model`, codul rămâne identic.
