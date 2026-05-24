"""
PromptRegistry — pattern din Lecția 2 (S3).

Idee: prompturile sunt CONFIGURAȚIE, nu cod. Le ținem în fișiere YAML
separate, încărcate de PromptRegistry care le rendăr cu Jinja2 când îi
ceri un prompt după nume.

Folosire:
    from prompts import get_prompt_registry
    registry = get_prompt_registry()
    text = registry.render("react_system", rol="expert juridic", domeniu="dreptul muncii")
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml
from jinja2 import Template


@dataclass(frozen=True)
class PromptTemplate:
    """Reprezentarea unui fișier YAML de prompt — imutabilă (frozen)."""
    name: str
    version: str
    prompt: str
    description: str = ""


class PromptRegistry:
    """Catalog central de prompturi încărcate din fișiere `.yaml`."""

    def __init__(self, folder: str | Path):
        self.folder = Path(folder)
        self._templates: dict[str, PromptTemplate] = {}
        self.reload()

    def reload(self) -> None:
        """Reîncarcă toate `.yaml` din folder (util în dev)."""
        templates: dict[str, PromptTemplate] = {}
        for path in self.folder.rglob("*.yaml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            tpl = PromptTemplate(
                name=data["name"],
                version=data["version"],
                prompt=data["prompt"],
                description=data.get("description", ""),
            )
            if tpl.name in templates:
                raise ValueError(
                    f"Prompt duplicat: '{tpl.name}' apare în mai multe YAML-uri"
                )
            templates[tpl.name] = tpl
        self._templates = templates

    def get(self, name: str) -> PromptTemplate:
        if name not in self._templates:
            raise KeyError(
                f"Prompt '{name}' nu există. Disponibile: {self.list_templates()}"
            )
        return self._templates[name]

    def render(self, name: str, **variabile) -> str:
        """Rendăr promptul cu Jinja2 + variabilele primite."""
        tpl = self.get(name)
        return Template(tpl.prompt).render(**variabile)

    def list_templates(self) -> list[str]:
        return sorted(self._templates.keys())


@lru_cache(maxsize=1)
def get_prompt_registry() -> PromptRegistry:
    """Singleton lazy — o singură instanță în toată aplicația."""
    folder = Path(__file__).parent
    return PromptRegistry(folder)
