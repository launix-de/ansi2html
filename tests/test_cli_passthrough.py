import sys
from io import StringIO
from unittest.mock import patch


def _import_local_converter():
    import importlib
    import os

    # Ensure we run the local project module, not any installed one
    mod_names = [k for k in list(sys.modules.keys()) if k.startswith("ansi2html")]
    for k in mod_names:
        sys.modules.pop(k, None)
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "src")))
    return importlib.import_module("ansi2html.converter")


@patch("sys.stdout", new_callable=StringIO)
def test_command_passthrough_pty_default(mock_stdout: StringIO) -> None:
    script = (
        "import sys; "
        "sys.stdout.write('\\x1b[31mRED\\x1b[0m\\n')"
    )
    conv = _import_local_converter()

    # In sandboxed CI there may be no PTY devices; emulate with a pipe
    import os as _os

    def _fake_openpty() -> tuple[int, int]:
        r, w = _os.pipe()
        return r, w

    from unittest.mock import patch as _patch
    with patch(
        "sys.argv",
        new=[
            "ansi2html",
            "python",
            "-c",
            script,
        ],
    ):
        with _patch.object(conv.pty, "openpty", side_effect=_fake_openpty):
            conv.main()
    out = mock_stdout.getvalue()
    assert "ansi31" in out
    assert "RED" in out


@patch("sys.stdout", new_callable=StringIO)
def test_command_passthrough_with_separator_and_inline(mock_stdout: StringIO) -> None:
    script = (
        "import sys; "
        "sys.stdout.write('\\x1b[31mRED\\x1b[0m')"
    )
    conv = _import_local_converter()

    import os as _os

    def _fake_openpty() -> tuple[int, int]:
        r, w = _os.pipe()
        return r, w

    from unittest.mock import patch as _patch
    with patch(
        "sys.argv",
        new=[
            "ansi2html",
            "--inline",
            "--",
            "python",
            "-c",
            script,
        ],
    ):
        with _patch.object(conv.pty, "openpty", side_effect=_fake_openpty):
            conv.main()
    out = mock_stdout.getvalue()
    # Inline mode should not include the full HTML template, but include styles
    assert "<html>" not in out
    assert "style=" in out or "#aa0000" in out or "ansi31" in out

