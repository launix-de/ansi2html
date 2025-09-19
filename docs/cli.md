## CLI: Command Passthrough (PTY)

`ansi2html` can run a command inside a pseudo‑terminal (PTY), capture its colored
output, and convert it to HTML. This makes tools that auto‑enable color when
attached to a TTY (like `git`) work without extra flags.

- Basic usage:

  ```shell
  ansi2html git log -p > git-log.html
  ```

- With explicit separator and options to `ansi2html`:

  ```shell
  ansi2html --inline -- git log -p > inline-git-log.html
  ```

- Produce a minimal inline snippet wrapped in a `<code>` element (no full HTML):

  ```shell
  echo $'\e[31mRED\e[0m' | ansi2html --standalone
  ```
  - Short form: `-S`

Behavior
- Arguments after `--` are always treated as the command to run.
- Without `--`, the first non-option token starts the command. All following
  tokens belong to the command, even if they start with `-`.
- The child process runs in a PTY and sees `TERM=xterm-256color`.

Pagers
- To prevent hangs with tools that auto‑page (e.g. `git` with `less`), ansi2html
  sets `GIT_PAGER=cat` and `PAGER=cat` by default in PTY mode. Set these
  explicitly to override, e.g. `GIT_PAGER=less -R`.

Inline vs Standalone
- `--inline`: emits only the converted content using inline styles (no `<html>`
  or `<style>` wrapper), suitable for embedding inside your own document.
- `--standalone`: like `--inline` but additionally wraps the output in a
  `<code style='white-space: pre;'>...</code>` element for convenience.

Notes
- This mode captures both stdout and stderr from the command and converts them
  together. If you need to separate them, prefer piping from the command into
  `ansi2html` instead of using passthrough mode.
