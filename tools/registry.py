"""
Tool Registry — pattern din Lecția 2 (S7).

Idee:
- TOOL_REGISTRY = dicționar global care reține toate tool-urile aplicației.
- @register_tool = decorator care, pus deasupra unei funcții, o validează
  și o adaugă AUTOMAT în registry la momentul importului.

Folosire în alt fișier:
    from tools.registry import register_tool
    from tools.params_models import CalculatorParams

    @register_tool
    def calculator(params: CalculatorParams) -> str:
        '''Evaluează o expresie matematică simplă.'''
        return str(eval(params.expression))
"""
from __future__ import annotations

import inspect
from typing import Callable, get_type_hints

from pydantic import BaseModel


# Dicționarul global — sursa unică de adevăr pentru toate tool-urile
TOOL_REGISTRY: dict[str, dict] = {}


def register_tool(func: Callable) -> Callable:
    """
    Decorator care validează signature + docstring și înregistrează
    funcția în TOOL_REGISTRY.

    Reguli aplicate:
    1. Funcția trebuie să aibă EXACT un parametru.
    2. Parametrul trebuie să fie de tip BaseModel (Pydantic).
    3. Docstring obligatoriu, minim 15 caractere (devine description-ul
       vizibil pentru LLM).
    """
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    # Validare 1: un singur parametru
    if len(params) != 1:
        raise TypeError(
            f"{func.__name__}: trebuie să aibă EXACT un parametru "
            f"(are {len(params)})."
        )

    # Validare 2: parametrul e BaseModel
    # NOTĂ: cu `from __future__ import annotations`, adnotările sunt string-uri.
    # get_type_hints() rezolvă string-urile înapoi în clase reale.
    type_hints = get_type_hints(func)
    param_name = params[0].name
    annotation = type_hints.get(param_name)
    if not (isinstance(annotation, type) and issubclass(annotation, BaseModel)):
        raise TypeError(
            f"{func.__name__}: parametrul trebuie să fie subclasă de "
            f"pydantic.BaseModel (e '{annotation}')."
        )

    # Validare 3: docstring prezent și suficient de descriptiv
    docstring = (func.__doc__ or "").strip()
    if not docstring:
        raise ValueError(
            f"{func.__name__}: docstring obligatoriu — devine description "
            f"vizibil pentru LLM."
        )
    if len(docstring) < 15:
        raise ValueError(
            f"{func.__name__}: docstring prea scurt ({len(docstring)} "
            f"caractere). LLM-ul are nevoie de min 15 ca să decidă când "
            f"să folosească tool-ul."
        )

    # Înregistrare în catalog
    if func.__name__ in TOOL_REGISTRY:
        raise ValueError(
            f"Tool duplicat: '{func.__name__}' e deja înregistrat."
        )

    TOOL_REGISTRY[func.__name__] = {
        "func": func,
        "params_model": annotation,
        "description": docstring,
    }

    return func  # decoratorul returnează funcția neschimbată
