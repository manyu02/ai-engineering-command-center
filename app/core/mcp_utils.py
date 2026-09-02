import json


def normalize_tool_result(result):
    if isinstance(result, dict):
        return result

    if isinstance(result, list):
        if len(result) == 1 and isinstance(result[0], dict):
            return result[0]

        if len(result) == 1 and isinstance(result[0], dict):
            text = result[0].get("text")

            if text:
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    pass

    if hasattr(result, "content"):
        return normalize_tool_result(result.content)

    raise TypeError(
        f"Unsupported MCP result type: {type(result).__name__}"
    )