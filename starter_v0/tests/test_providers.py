from pathlib import Path

from providers.openai_provider import coerce_args
from tools import load_tool_declarations, to_openai_tools

TOOLS = to_openai_tools(load_tool_declarations(Path(__file__).resolve().parent.parent / "artifacts" / "tools.yaml"))


def test_coerce_args_converts_string_numbers_and_booleans_per_schema():
    assert coerce_args({"screenname": "elonmusk", "limit": "10"}, "timeline", TOOLS) == {"screenname": "elonmusk", "limit": 10}
    assert coerce_args({"text": "hi", "confirmed": "True"}, "send", TOOLS) == {"text": "hi", "confirmed": True}


def test_coerce_args_leaves_strings_and_unknown_values_alone():
    assert coerce_args({"query": "10", "max_results": "ten"}, "lookup", TOOLS) == {"query": "10", "max_results": "ten"}
    assert coerce_args({"limit": "5"}, "no_such_tool", TOOLS) == {"limit": "5"}
