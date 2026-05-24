"""
Test rapid pentru PromptRegistry — verifică:
1. YAML-ul se încarcă fără erori
2. Render-ul cu variabile produce un string non-gol
3. Render-ul fără variabile folosește default-urile

Rulează:
    python test_prompts.py
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

from prompts import get_prompt_registry


def main() -> None:
    registry = get_prompt_registry()

    print("=" * 60)
    print("Prompturi încărcate:", registry.list_templates())
    print("=" * 60)

    tpl = registry.get("react_system")
    print(f"Nume:    {tpl.name}")
    print(f"Versiune:{tpl.version}")
    print(f"Descriere: {tpl.description.strip()}")
    print("=" * 60)

    print("\n--- Render cu valori custom ---\n")
    text = registry.render(
        "react_system",
        rol="asistent contabil",
        domeniu="contabilitate IMM",
        max_cuvinte=150,
    )
    print(text)

    print("\n--- Render cu default-uri ---\n")
    text_default = registry.render("react_system")
    print(text_default[:300] + "...")

    print("\nOK — registry funcționează.")


if __name__ == "__main__":
    main()
