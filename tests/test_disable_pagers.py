import os
import sys
from io import StringIO
from unittest.mock import patch


def _import_local_converter():
    import importlib
    import os as _os

    # Ensure we run the local project module, not any installed one
    mod_names = [k for k in list(sys.modules.keys()) if k.startswith("ansi2html")]
    for k in mod_names:
        sys.modules.pop(k, None)
    sys.path.insert(0, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), os.pardir, "src")))
    return importlib.import_module("ansi2html.converter")


@patch("sys.stdout", new_callable=StringIO)
def test_sets_git_pager_to_cat(mock_stdout: StringIO) -> None:
    conv = _import_local_converter()

    # Make sure no pre-existing env overrides the default we set
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("GIT_PAGER", None)
        # Use a simple python subprocess to echo the env var value
        script = (
            "import os, sys; sys.stdout.write(os.environ.get('GIT_PAGER', 'NONE'))"
        )

        # Emulate PTY with a pipe to keep the test environment simple
        import os as _os

        def _fake_openpty() -> tuple[int, int]:
            r, w = _os.pipe()
            return r, w

        from unittest.mock import patch as _patch
        with _patch(
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

    # Our default should have been applied; content is wrapped in HTML
    assert "cat" in mock_stdout.getvalue()
