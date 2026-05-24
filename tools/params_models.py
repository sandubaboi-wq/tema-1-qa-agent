"""
Pydantic BaseModel pentru fiecare tool al agentului.

Pydantic validează automat tipurile și constrângerile ÎNAINTE
ca funcția tool-ului să fie apelată. Asta înseamnă:
- Tipuri greșite → eroare clară, ÎNAINTE de execuție
- Valori în afara range-ului → eroare clară
- Descrierile din Field() ajung la LLM (devin JSON Schema)
"""
from pydantic import BaseModel, Field


class CalculatorParams(BaseModel):
  """Parametrii pentru tool-ul calculator."""
  expression: str = Field(
      description="Expresia matematică de evaluat (ex: '2 + 3 * 4', '847 * 0.19').",
      min_length=1,
  )


class DatetimeParams(BaseModel):
      """Parametrii pentru tool-ul de dată/oră curentă."""
      timezone: str = Field(
          default="Europe/Bucharest",
          description="Fusul orar IANA (ex: 'Europe/Bucharest', 'UTC').",
      )


class WebSearchParams(BaseModel):
    """Parametrii pentru tool-ul web_search (mock în Tema 1)."""
    query: str = Field(
      description="Termenii de căutat pe web.",
      min_length=2,
    )
    max_results: int = Field(
      default=5,
      description="Numărul maxim de rezultate returnate.",
      ge=1,
      le=20,
    )