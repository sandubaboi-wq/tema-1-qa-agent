"""
Pachetul `tools` — API public pentru agent.

Import-ul `from tools import basic_tools` forțează rularea decoratoarelor
@register_tool, care la rândul lor populează TOOL_REGISTRY.
Fără acest import, registry-ul ar rămâne gol.
"""
from .registry import TOOL_REGISTRY, register_tool
from .tool_wrapper import ToolWrapper

# Import basic_tools pentru efect secundar — înregistrează cele 3 tool-uri
from . import basic_tools  # noqa: F401

__all__ = ["TOOL_REGISTRY", "register_tool", "ToolWrapper"]
