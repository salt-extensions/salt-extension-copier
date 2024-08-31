DARKGREEN = (0, 100, 0)
DARKRED = (139, 0, 0)
YELLOW = (255, 255, 0)


def pprint(msg, bold=False, fg=None, bg=None):
    """
    Ugly helper for printing a bit more fancy output.
    Stand-in for questionary/prompt_toolkit.
    """
    out = ""
    if bold:
        out += "\033[1m"
    if fg:
        red, green, blue = fg
        out += f"\033[38;2;{red};{green};{blue}m"
    if bg:
        red, green, blue = bg
        out += f"\033[48;2;{red};{green};{blue}m"
    out += msg
    if bold or fg or bg:
        out += "\033[0m"
    print(out)


def status(msg, message=None):
    out = f"\n    → {msg}"
    pprint(out, bold=True, fg=DARKGREEN)
    if message:
        pprint(message)


def warn(header, message=None):
    out = f"\n{header}"
    pprint(out, bold=True, bg=DARKRED)
    if message:
        pprint(message)
