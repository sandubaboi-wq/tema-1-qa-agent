"""
ToolWrapper — punctul unic de execuție și expunere a tool-urilor.

Două operații principale:
- call(name, args) → validează cu Pydantic, execută, returnează rezultatul ca string
- catalog_anthropic() → generează lista de tools în format JSON Schema pentru LLM

Erorile (tool inexistent, params invalizi, execuție eșuată) sunt CAPTURATE
și returnate ca string descriptiv — LLM-ul nu vede excepții raw, vede mesaje
human-readable pe care le poate folosi în următoarea iterație ReAct.
"""
from __future__ import annotations

from pydantic import ValidationError

from .registry import TOOL_REGISTRY


class ToolWrapper:
    """Interfața standard prin care agentul cere execuția unui tool."""

    @staticmethod
    def call(name: str, args: dict) -> str:
        """
        Apelează un tool după nume, cu argumentele primite de la LLM.

        Returnează MEREU un string — succes sau eroare.
        Nu lasă excepții să iasă din funcție.
        """
        # 1. Lookup în registry
        if name not in TOOL_REGISTRY:
            return (
                f"Eroare: tool-ul '{name}' nu există. "
                f"Disponibile: {sorted(TOOL_REGISTRY.keys())}."
            )

        tool = TOOL_REGISTRY[name]
        params_model = tool["params_model"]
        func = tool["func"]

        # 2. Validare cu Pydantic
        try:
            params = params_model(**args)
        except ValidationError as e:
            return (
                f"Eroare validare pentru '{name}': "
                f"argumentele nu respectă schema. Detalii: {e.errors()}"
            )

        # 3. Execuție — capturăm orice eșec
        try:
            return str(func(params))
        except Exception as e:
            return f"Eroare execuție '{name}': {type(e).__name__}: {e}"

    @staticmethod
    def catalog_anthropic() -> list[dict]:
        """
        Generează lista de tools în format Anthropic.
        Fiecare tool e descris ca dict cu: name, description, input_schema.

        LLM-ul Anthropic primește această listă și știe ce poate apela.
        """
        catalog = []
        for name, tool in TOOL_REGISTRY.items():
            catalog.append({
                "name": name,
                "description": tool["description"],
                "input_schema": tool["params_model"].model_json_schema(),
            })
        return catalog

    @staticmethod
    def catalog_openai() -> list[dict]:
        """
        Variantă pentru format OpenAI (folosit și de LiteLLM, qwen, gemma etc.).
        Diferența față de Anthropic: tools sunt împachetate sub {"type": "function", "function": {...}}.
        """
        catalog = []
        for name, tool in TOOL_REGISTRY.items():
            catalog.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool["description"],
                    "parameters": tool["params_model"].model_json_schema(),
                },
            })
        return catalog
