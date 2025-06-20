def bold(text: any) -> str:
    """Return text formatted in bold."""
    return f"\033[1m{text}\033[0m"


def green(text: any) -> str:
    """Return text formatted in green."""
    return f"\033[32m{str(text)}\033[0m"


def indent(text: str, tabs: int = 1) -> str:
    """Indent text with a specified number of tabs."""
    return "\t" * tabs + text
