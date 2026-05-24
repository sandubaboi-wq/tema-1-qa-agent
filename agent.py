"""
Agent ReAct — Tema 1.

Pattern: Think → Act → Observe → Repeat → Answer.
LLM-ul cere tool-uri, aplicația le execută, rezultatele se întorc la LLM,
care decide următoarea acțiune. Bucla se oprește când LLM-ul răspunde
fără să mai ceară tools, sau la max_iterations.

Conectare: prin LiteLLM proxy pe `localhost:4000` (default), care rutează
către modele Ollama (qwen, mistral, llama etc.) pe Oracle VM via SSH tunnel.

Folosire:
    python agent.py                          # mod interactiv (CLI)
    from agent import chat; chat("...")      # mod programatic
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from prompts import get_prompt_registry
from tools import ToolWrapper


# Încarcă .env din rădăcina Cod_Curs (unde stau cheile reale)
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ENV_PATH)


# ============================================================
# Configurare — override-uri prin variabile de mediu
# ============================================================
# LLM_PROVIDER alege backend-ul: "litellm" (default, gratis pe VM) sau "anthropic" (rapid, plătit)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "litellm").lower()


def _provider_defaults() -> tuple[str, str, str]:
    """Returnează (base_url, api_key, model) potrivite pentru provider-ul ales."""
    if LLM_PROVIDER == "anthropic":
        return (
            "https://api.anthropic.com/v1/",
            os.getenv("ANTHROPIC_API_KEY", ""),
            os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-haiku-4-5-20251001"),
        )
    # LiteLLM pe VM (default)
    return (
        "http://localhost:4000/v1",
        "local",
        "qwen",
    )


_DEFAULT_BASE_URL, _DEFAULT_API_KEY, _DEFAULT_MODEL = _provider_defaults()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", _DEFAULT_BASE_URL)
LLM_API_KEY = os.getenv("LLM_API_KEY", _DEFAULT_API_KEY)
LLM_MODEL = os.getenv("LLM_MODEL", _DEFAULT_MODEL)
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))


# ============================================================
# Client LLM — un singur loc de creat (Factory mic)
# ============================================================
def create_llm_client() -> OpenAI:
    """
    Construiește clientul OpenAI.

    Anthropic oferă un endpoint OpenAI-compatible la
    https://api.anthropic.com/v1/ — folosim același OpenAI SDK pentru
    ambii provideri, doar schimbăm base_url + api_key + model.
    """
    if not LLM_API_KEY:
        raise RuntimeError(
            f"LLM_API_KEY lipsește pentru provider-ul '{LLM_PROVIDER}'. "
            f"Verifică .env."
        )
    return OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)


# ============================================================
# Bucla ReAct
# ============================================================
def react_loop(
    client: OpenAI,
    messages: list[dict],
    model: str = LLM_MODEL,
    max_iterations: int = MAX_ITERATIONS,
    verbose: bool = True,
) -> str:
    """
    Rulează bucla ReAct: Think → Act → Observe → Repeat.

    Args:
        client: client OpenAI configurat
        messages: lista inițială de mesaje (system + user)
        model: numele modelului (qwen, mistral, llama, etc.)
        max_iterations: safety net — oprește bucla după N iterații
        verbose: dacă True, afișează ce face agentul la fiecare pas

    Returns:
        Răspunsul final ca string.

    Raises:
        RuntimeError dacă max_iterations e atins fără răspuns final.
    """
    tools_catalog = ToolWrapper.catalog_openai()
    last_tool_signature = None
    repeat_count = 0

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n[Iter {iteration}/{max_iterations}] LLM gândește...")

        # THINK: LLM-ul analizează contextul
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools_catalog,
        )
        message = response.choices[0].message

        # Salvăm răspunsul LLM în istoric (necesar pentru next iteration)
        messages.append(message.model_dump(exclude_none=True))

        # Verificăm dacă LLM-ul a cerut tool-uri sau a răspuns direct
        if not message.tool_calls:
            if verbose:
                print(f"[Iter {iteration}] LLM a răspuns direct.")
            return message.content or ""

        # ACT + OBSERVE: executăm fiecare tool cerut și pasăm rezultatul înapoi
        if verbose:
            tool_names = [tc.function.name for tc in message.tool_calls]
            print(f"[Iter {iteration}] LLM cere tools: {tool_names}")

        # Detecție loop infinit — același tool + aceleași args de 3+ ori la rând
        current_signature = tuple(
            (tc.function.name, tc.function.arguments) for tc in message.tool_calls
        )
        if current_signature == last_tool_signature:
            repeat_count += 1
            if repeat_count >= 2:  # 3 apeluri identice consecutive
                if verbose:
                    print(f"[Iter {iteration}] ⚠️ Loop detectat — oprire forțată.")
                return (
                    "Nu am putut formula un răspuns final — modelul a intrat în "
                    "loop apelând repetat același tool. Încearcă un model mai "
                    "mare (mistral) sau o întrebare mai specifică."
                )
        else:
            last_tool_signature = current_signature
            repeat_count = 0

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                result = f"Eroare parsare argumente JSON: {e}"
            else:
                result = ToolWrapper.call(name, args)

            if verbose:
                print(f"  {name}({args}) → {result[:100]}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    raise RuntimeError(
        f"max_iterations ({max_iterations}) atins fără răspuns final."
    )


# ============================================================
# Interfața publică
# ============================================================
def chat(
    question: str,
    rol: str = "un asistent expert generalist",
    domeniu: str = "Q&A factual cu acces la tool-uri",
    model: str = LLM_MODEL,
    verbose: bool = True,
) -> str:
    """
    Trimite o întrebare către agent, primește răspuns final.

    Asamblează system prompt-ul din PromptRegistry și rulează bucla ReAct.
    """
    registry = get_prompt_registry()
    system_prompt = registry.render(
        "react_system",
        rol=rol,
        domeniu=domeniu,
        max_cuvinte=200,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    client = create_llm_client()
    return react_loop(client, messages, model=model, verbose=verbose)


# ============================================================
# Mod interactiv CLI
# ============================================================
def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print(f"Agent ReAct — Tema 1")
    print(f"Provider: {LLM_PROVIDER} | Model: {LLM_MODEL}")
    print(f"Base URL: {LLM_BASE_URL}")
    print(f"Tools disponibile: {[t['function']['name'] for t in ToolWrapper.catalog_openai()]}")
    print("=" * 60)
    print("Tastează întrebări. 'iesi' / 'exit' / Ctrl+C pentru închidere.\n")

    while True:
        try:
            question = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nLa revedere.")
            break

        if not question:
            continue
        if question.lower() in ("iesi", "exit", "quit"):
            print("La revedere.")
            break

        try:
            answer = chat(question)
            print(f"\n=== RĂSPUNS ===\n{answer}\n")
        except Exception as e:
            print(f"\n[Eroare] {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    main()
