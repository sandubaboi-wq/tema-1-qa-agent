"""
Test rapid pentru Pasul 2 — Tools cu Pydantic.

Verifică:
1. Cele 3 tool-uri sunt înregistrate
2. Apel cu params VALIZI → returnează rezultat corect
3. Apel cu params INVALIZI → mesaj de eroare clar (Pydantic)
4. Apel cu nume INEXISTENT → mesaj de eroare clar
5. Apel cu execuție eșuată → mesaj de eroare clar (try/except)
6. Catalogul Anthropic e bine format

Rulează:
    python test_tools.py
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

from tools import TOOL_REGISTRY, ToolWrapper


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


def main() -> None:
    # ---------- 1. Tool-urile sunt înregistrate ----------
    section("1. Înregistrare automată")
    print("Tool-uri în registry:", sorted(TOOL_REGISTRY.keys()))
    assert set(TOOL_REGISTRY.keys()) == {
        "calculator", "get_current_datetime", "web_search"
    }, "Lipsesc tool-uri!"
    print("OK — toate 3 sunt prezente.")

    # ---------- 2. Apel cu params valizi ----------
    section("2. Apel cu params valizi")

    r1 = ToolWrapper.call("calculator", {"expression": "1847 * 394"})
    print(f"calculator(1847*394) → {r1}")
    assert r1 == "727718", f"Aștept 727718, primit {r1}"

    r2 = ToolWrapper.call("get_current_datetime", {})
    print(f"get_current_datetime() → {r2}")
    assert "2026" in r2, "Anul ar trebui să fie 2026"

    r3 = ToolWrapper.call("web_search", {"query": "exemplu", "max_results": 2})
    print(f"web_search('exemplu', 2) →\n{r3}")
    assert "Rezultate pentru 'exemplu'" in r3

    print("OK — toate 3 apeluri reușesc.")

    # ---------- 3. Apel cu params INVALIZI (Pydantic respinge) ----------
    section("3. Params invalizi — mesaj clar de eroare")

    r = ToolWrapper.call("web_search", {"query": "x", "max_results": 99})
    print(f"web_search('x', 99) → {r}")
    assert "Eroare validare" in r, "Trebuia să fie eroare Pydantic"
    print("OK — Pydantic a respins corect.")

    # ---------- 4. Tool inexistent ----------
    section("4. Tool inexistent — mesaj clar de eroare")
    r = ToolWrapper.call("nu_exista_tool", {})
    print(f"call('nu_exista_tool') → {r}")
    assert "nu există" in r
    print("OK — eroare clară pentru nume greșit.")

    # ---------- 5. Execuție eșuată (împărțire la zero) ----------
    section("5. Execuție eșuată — capturată cu try/except")
    r = ToolWrapper.call("calculator", {"expression": "10 / 0"})
    print(f"calculator(10/0) → {r}")
    assert "Eroare" in r
    print("OK — eroarea nu a stricat aplicația.")

    # ---------- 6. Catalog pentru LLM ----------
    section("6. Catalog JSON Schema pentru LLM")
    cat_anthropic = ToolWrapper.catalog_anthropic()
    print(f"Catalog Anthropic — {len(cat_anthropic)} tools")
    for t in cat_anthropic:
        print(f"  - {t['name']}: {t['description'][:60]}...")
    assert len(cat_anthropic) == 3

    cat_openai = ToolWrapper.catalog_openai()
    print(f"Catalog OpenAI    — {len(cat_openai)} tools")
    assert all(t["type"] == "function" for t in cat_openai)
    print("OK — ambele formate (Anthropic + OpenAI) generate corect.")

    section("✅ TOATE TESTELE TREC")


if __name__ == "__main__":
    main()
