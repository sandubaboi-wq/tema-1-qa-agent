"""Generator PDF predare Tema 1 — Skillab AI Agent Development."""
from fpdf import FPDF
from pathlib import Path

OUT = Path(__file__).parent / "Tema_1_Sandu_Baboi.pdf"

pdf = FPDF(format="A4")
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_margins(15, 15, 15)

def h1(txt):
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(180, 8, txt, ln=1)
    pdf.ln(2)

def h2(txt):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(180, 6, txt, ln=1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)

def p(txt):
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_x(15); pdf.multi_cell(180, 4.6, txt)
    pdf.ln(1)

def bullet(items):
    pdf.set_font("Helvetica", "", 9.5)
    for it in items:
        pdf.set_x(15)
        pdf.multi_cell(180, 4.6, "  - " + it)
    pdf.ln(1)

def safe_cell(txt, h=5):
    pdf.set_x(15)
    pdf.multi_cell(180, h, txt)

def code(txt):
    pdf.set_font("Courier", "", 8.5)
    pdf.set_fill_color(245, 245, 245)
    for line in txt.splitlines():
        pdf.cell(180, 4.5, "  " + line, ln=1, fill=True)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.ln(1)

def table(rows, widths):
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(230, 230, 230)
    for w, h in zip(widths, rows[0]):
        pdf.cell(w, 6, h, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for row in rows[1:]:
        for w, c in zip(widths, row):
            pdf.cell(w, 5.5, c, border=1)
        pdf.ln()
    pdf.ln(2)

# ---------- Header ----------
h1("Tema 1 - Agent QA cu Tools + Prompts + ReAct")
pdf.set_font("Helvetica", "", 10)
pdf.cell(180, 5, "Autor: Sandu Baboi  |  Curs: AI Agent Development @ Skillab  |  Lector: Richard Francu", ln=1)
pdf.cell(180, 5, "Data predare: 26 mai 2026  |  Sesiunea L2 - Instrumente, prompturi si observabilitate", ln=1)
pdf.ln(3)

# ---------- Repo ----------
h2("Repository GitHub (predare prin Git push conform cerintei lectorului)")
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(0, 0, 180)
pdf.cell(180, 5, "https://github.com/sandubaboi-wq/tema-1-qa-agent", ln=1, link="https://github.com/sandubaboi-wq/tema-1-qa-agent")
pdf.set_text_color(0, 0, 0)
p("Username Git: sandubaboi-wq  |  Branch: main  |  Commit predare: 9910041")
pdf.ln(1)

# ---------- Ce am implementat ----------
h2("Ce am implementat")
bullet([
    "Agent ReAct (Reasoning + Acting) cu bucla think -> act -> observe -> repeat (max 10 iteratii).",
    "Tool Registry cu 3 tool-uri validate prin Pydantic: calculator (ast.parse, fara eval), get_current_datetime (timezone IANA), web_search (mock).",
    "Prompt Registry cu prompturi YAML + placeholder-uri Jinja2 + singleton lazy via @lru_cache.",
    "Factory pattern pentru client LLM - suporta 2 provideri (Anthropic, LiteLLM proxy) prin variabila de mediu, fara modificari de cod.",
    "Catalog tool-uri exportat in 2 formate (OpenAI function calling + Anthropic tool use) pentru compatibilitate cu orice provider.",
])

# ---------- Pattern-uri din L2 ----------
h2("Pattern-uri din Lectia 2 aplicate")
table([
    ["Pattern", "Locatie in cod", "Slide L2"],
    ["Prompt Registry", "prompts/registry.py", "S3"],
    ["Decorator (@register_tool)", "tools/registry.py", "S4.3"],
    ["Factory (create_llm_client)", "agent.py", "S4.4"],
    ["Singleton lazy (@lru_cache)", "prompts/registry.py", "S4.6"],
    ["Tool Registry + Wrapper", "tools/", "S7"],
    ["ReAct loop", "agent.py:react_loop", "S6"],
], widths=[55, 70, 25])

# ---------- Structura ----------
h2("Structura proiect")
code("""tema_1/
  prompts/                 # Prompturile sunt CONFIGURATIE, nu cod
    react_system.yaml      # System prompt cu placeholder-uri Jinja2
    registry.py            # PromptRegistry (singleton lazy)
  tools/                   # Tool Registry
    params_models.py       # Pydantic BaseModel per tool
    registry.py            # TOOL_REGISTRY + @register_tool
    basic_tools.py         # calculator, datetime, web_search
    tool_wrapper.py        # ToolWrapper.call() + catalog
  agent.py                 # Bucla ReAct + factory client LLM
  test_prompts.py          # 3 verificari PromptRegistry
  test_tools.py            # 6 verificari Tools cu Pydantic
  test_agent.py            # 5 scenarii end-to-end
  README.md / requirements.txt""")

# ---------- Rulare ----------
h2("Rulare")
code("""python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt

# Provider Anthropic
set LLM_PROVIDER=anthropic
set ANTHROPIC_API_KEY=sk-ant-...

# SAU provider LiteLLM (gratuit, local)
set LLM_PROVIDER=litellm

python agent.py                # mod interactiv CLI
python test_prompts.py         # test PromptRegistry
python test_tools.py           # test Tools cu Pydantic
python test_agent.py           # test Agent end-to-end""")

# ---------- Anti-patterns evitate ----------
h2("Anti-patterns evitate (robustete)")
bullet([
    "eval() pentru calculator inlocuit cu ast.parse + whitelist operatori (siguranta).",
    "Loop infinit la tool calls: detectie repetitie identica + max_iterations=10.",
    "Erori raw spre LLM: toate erorile sunt capturate si transformate in dict {success, error} cu mesaj human-readable.",
    "Tool-urile NU arunca exceptii - returneaza mereu dict, agentul decide pasul urmator.",
])

pdf.ln(2)
pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 4, "Predat conform cerintei lectorului prin Git push pe repo privat. Acest PDF este dovada operationala pentru LMS.", ln=1)

pdf.output(str(OUT))
print(f"OK: {OUT} ({OUT.stat().st_size} bytes)")
