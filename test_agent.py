"""
Test agent ReAct — 5 scenarii.

ATENȚIE: necesită tunelul SSH activ + LiteLLM rulând pe VM:
    ssh -N -L 4000:localhost:4000 skillab

Rulează:
    python test_agent.py
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

import httpx

from agent import chat, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


def check_backend_alive() -> bool:
    """Verifică dacă backend-ul răspunde înainte să pornim testele."""
    if LLM_PROVIDER == "litellm":
        try:
            r = httpx.get(
                f"{LLM_BASE_URL.replace('/v1', '')}/health/liveliness",
                timeout=5.0,
            )
            return r.status_code == 200
        except Exception:
            return False
    # Anthropic: nu verificăm health explicit, doar trecem mai departe
    return True


def main() -> None:
    section("0. Verificare conexiune")
    if not check_backend_alive():
        print(f"❌ Backend ({LLM_PROVIDER}) nu răspunde.")
        if LLM_PROVIDER == "litellm":
            print("Deschide tunelul SSH în alt PowerShell:")
            print("  ssh -N -L 4000:localhost:4000 skillab")
        sys.exit(1)
    print(f"✅ Provider: {LLM_PROVIDER} | Model: {LLM_MODEL}")

    # ---------- Scenariul 1: răspuns direct, fără tool ----------
    section("1. Răspuns direct (fără tool)")
    ans = chat("Salut! Spune-mi în 1 propoziție cine ești.", verbose=False)
    print(f"Q: Salut! Cine ești?")
    print(f"A: {ans}")

    # ---------- Scenariul 2: calculator ----------
    section("2. Calculator — 1847 × 394")
    ans = chat("Cât face 1847 înmulțit cu 394?", verbose=True)
    print(f"\nA: {ans}")
    if "727718" in ans or "727,718" in ans:
        print("✅ Calculul e corect.")
    else:
        print("⚠️  Răspunsul nu conține 727718 — verifică manual.")

    # ---------- Scenariul 3: datetime ----------
    section("3. Datetime — data curentă")
    ans = chat("Ce dată și oră este acum în România?", verbose=True)
    print(f"\nA: {ans}")
    if "2026" in ans:
        print("✅ Răspunsul conține anul 2026.")
    else:
        print("⚠️  Verifică dacă răspunsul are dată curentă.")

    # ---------- Scenariul 4: multi-step ----------
    section("4. Multi-step — câte zile până la 1 iunie 2026")
    ans = chat(
        "Câte zile sunt din ziua de azi până pe 1 iunie 2026? "
        "Folosește calculator pentru diferență.",
        verbose=True,
    )
    print(f"\nA: {ans}")

    # ---------- Scenariul 5: web_search ----------
    section("5. Web search (mock)")
    ans = chat(
        "Caută informații despre 'Python AI agents' și rezumă în 2 fraze.",
        verbose=True,
    )
    print(f"\nA: {ans}")

    section("✅ TESTE TERMINATE")
    print("Verifică manual răspunsurile — modelele locale nu sunt mereu perfecte.")
    print("Important pentru Tema 1: bucla ReAct funcționează + tool calls se execută corect.")


if __name__ == "__main__":
    main()
