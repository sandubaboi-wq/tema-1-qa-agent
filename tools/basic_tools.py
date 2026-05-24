"""
Cele 3 tool-uri concrete ale agentului:
- calculator       — evaluare expresii matematice (sigur, fără eval direct)
- get_current_datetime — data/ora curentă într-un fus orar
- web_search       — mock (în Tema 1 returnăm rezultate fake, ca să nu cheltuim API)

Toate sunt înregistrate AUTOMAT în TOOL_REGISTRY prin @register_tool.
"""
from __future__ import annotations

import ast
import operator
from datetime import datetime
from zoneinfo import ZoneInfo

from .params_models import CalculatorParams, DatetimeParams, WebSearchParams
from .registry import register_tool


# ============================================================
# 1. CALCULATOR — fără eval() periculos
# ============================================================

# Doar operatorii matematici siguri sunt permiși
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    """Evaluare recursivă a unui AST matematic — refuză orice non-numeric."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        op = _SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Operator nepermis: {type(node.op).__name__}")
        return op(_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Operator unar nepermis: {type(node.op).__name__}")
        return op(_safe_eval(node.operand))
    raise ValueError(f"Element AST nepermis: {type(node).__name__}")


@register_tool
def calculator(params: CalculatorParams) -> str:
    """Evaluează o expresie matematică simplă cu operatori +, -, *, /, **, %.

    Folosește tool-ul pentru calcule cu mai mult de 2 cifre sau cu zecimale.
    Nu accepta funcții, variabile sau cod arbitrar — doar aritmetică.
    Exemple valide: '2+3*4', '1847*394', '(100+250)*0.19'.
    """
    try:
        tree = ast.parse(params.expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except (ValueError, SyntaxError) as e:
        return f"Eroare calcul: {e}"


# ============================================================
# 2. GET CURRENT DATETIME
# ============================================================

@register_tool
def get_current_datetime(params: DatetimeParams) -> str:
    """Returnează data și ora curentă într-un fus orar specificat.

    Folosește tool-ul ori de câte ori ai nevoie de data sau ora exactă.
    Default fus orar: Europe/Bucharest. Format ISO 8601.
    Exemple de timezone valide: 'Europe/Bucharest', 'UTC', 'America/New_York'.
    """
    try:
        tz = ZoneInfo(params.timezone)
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return f"Eroare datetime: {e}"


# ============================================================
# 3. WEB SEARCH — MOCK pentru Tema 1
# ============================================================

# Mock-uri simple: query → listă de "rezultate" inventate
_MOCK_SEARCH_DATA: dict[str, list[dict]] = {
    "default": [
        {"title": "Rezultat 1", "snippet": "Conținut placeholder pentru demo."},
        {"title": "Rezultat 2", "snippet": "Al doilea rezultat fake."},
        {"title": "Rezultat 3", "snippet": "Al treilea rezultat fake."},
    ],
}


@register_tool
def web_search(params: WebSearchParams) -> str:
    """Caută pe web și returnează primele rezultate (titlu + snippet).

    NOTĂ: în Tema 1 e MOCK — întoarce date fake pentru demonstrație.
    Folosește tool-ul pentru întrebări despre fapte recente sau date externe.
    Nu folosi pentru calcule sau opinii.
    """
    results = _MOCK_SEARCH_DATA.get(params.query.lower(), _MOCK_SEARCH_DATA["default"])
    results = results[: params.max_results]
    lines = [f"Rezultate pentru '{params.query}':"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']} — {r['snippet']}")
    return "\n".join(lines)
