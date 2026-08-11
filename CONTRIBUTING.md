# Contributing to this Project
**Here's how you can help.**

## Process
In the spirit of openness, this project follows [the Forking Flow](http://www.dalescott.net/wordpress/?p=1266), a derivative of [the Gitflow model](http://nvie.com/posts/a-successful-git-branching-model/).  We use Pull Requests to develop conversations around ideas, and turn ideas into actions.

**Some PR Basics**
- Anyone can submit a Pull Request with changes they'd like to see made.
- Pull Requests should attempt to solve a single [1], clearly defined problem [2].
- Everyone should submit Pull Requests early (within the first few commits), so everyone on the team is aware of the direction you're taking.
- Authors are responsible for explicitly tagging anyone who might be impacted by the pull request and get the recipient's sign-off [3].
- The Pull Request should serve as the authority on the status of a change, so everyone on the team is aware of the plan of action.
- Relevant domain authority _must_ sign-off on a pull request before it is merged [4].
- Anyone _except_ the author can merge a pull request once all sign-offs are complete.

[1]: if there are multiple problems you're solving, it is recommended that you create a branch for each.  For example, if you are implementing a small change and realize you want to refactor an entire function, you might want to implement the refactor as your first branch (and pull request), then create a new branch (and pull request) from the refactor to implement your new _feature_.  This helps resolve merge conflicts and separates out the logical components of the decision-making process.  
[2]: include a description of the problem that is being resolved in the description field, or a reference to the issue number where the problem is reported.  Examples include; "Follow Button doesn't Reflect State of Follow" or "Copy on Front-page is Converting Poorly".  
[3]: notably, document the outcome of any out-of-band conversations in the pull request.  
[4]: changes to marketing copy, for example, must be approved by the authority on marketing.

## Coding Conventions
Detail and examples below; here are the basic principles.

### tl;dr
- In general, Python [PEP 8](https://www.python.org/dev/peps/pep-0008/) should be followed.
- Beyond that the [Google Python style guide](https://google.github.io/styleguide/pyguide.html) should be followed when possible.
- All new functions and parameters (including cleaners, convertors, and validators) should be added to the documentation.
- Examples of all new functions and parameters (including cleaners, convertors, and validators) should be added to the examples.

## Running the tests

Install the package with its test extra, then run `pytest` with no arguments:

```
pip install -e ".[test]"
pytest
```

`testpaths` in `pyproject.toml` is the single collection root, so `pytest`, `tox` and CI
all collect exactly the same tests. Pass a path only to narrow a run
(`pytest cooked_input/tests/test_cleaners.py -k choice`).

For coverage:

```
pytest --cov --cov-report=term-missing
```

### The coverage ratchet

CI runs `pytest --cov --cov-fail-under=<floor>` in its own job. **That number only ever
goes up, and it goes up in the PR that earns the increase.** Never lower it to make a red
build green — if a change drops coverage, either the change needs a test or the drop needs
explaining in the PR.

The floor starts below the measured baseline rather than at the project's 97% target, so
that every PR along the way can be green on its own. Raise it by the whole amount a PR
gains; leaving it slack lets the next regression hide.

The floor is **99%**, not 100%, even though the package currently measures 100%. A 100%
gate means every future line needs either a test or a `# pragma: no cover`, and the usual
outcome is that pragmas accumulate until the number stops meaning anything. 99% keeps
essentially all of the value and leaves room for one genuinely awkward line.

Coverage is deliberately not in `addopts` — it would slow all eight matrix jobs and every
local run for no benefit.

### Type checking

Install the tools and run both, from the repository root:

```
pip install -e ".[test,typecheck]"
ruff check
ty check
```

**Two tools, two jobs.** `ty` checks that the annotations are *correct*. It has no
equivalent of mypy's `--disallow-untyped-defs`, so it cannot tell you a function was
missed — Ruff's `ANN` rules do that. Neither alone is enough, so the `types` CI job runs
both and Ruff goes first: "you forgot to annotate this" is the more actionable failure.

`ty` is pinned to an exact version in the `typecheck` extra rather than floored. It is
pre-1.0, and its diagnostics change between releases; an unpinned checker turns CI red on
someone else's release schedule. Bump the pin deliberately, in its own commit, so that a
new checker's findings are never mixed into an unrelated change.

**The annotation ratchet.** `per-file-ignores` in `pyproject.toml` lists the modules that
are not yet annotated. Like the coverage floor, that list only ever shrinks, and it shrinks
in the PR that types the module. Never add a module back to it.

Tests and examples are exempt from `ANN` by policy — annotations buy little in a test, and
the examples are demo scripts rather than library code. `ty` still checks the tests, and
that is deliberate: the suite calls the public API several hundred times from the outside,
which is the cheapest validation the annotations get.

`Any` is allowed (`ANN401` is off). `cooked_input` converts unknown console text into
whatever the caller asked for, so `Any` is sometimes the honest annotation — the `**options`
bags and `Convertor.__call__` especially. Prefer a real type wherever one exists.

### Docstrings do not restate types

Write `:param precision:`, never `:param int precision:`, and do not write `:rtype:` at all.
The docs build runs [`sphinx-autodoc-typehints`](https://github.com/tox-dev/sphinx-autodoc-typehints),
which renders each parameter's type and the return type from the signature. A type written in
a docstring as well is not merely redundant — it *wins*, so it silently shadows the annotation
and is free to drift out of date. Several did: `get_int` was documented `:rtype: int` long
after it had learned to return `None` for a blank optional response.

Say in prose what the annotation cannot. Where the honest annotation is `Any` — `get_input`,
`process_value`, `Convertor.__call__` — the `:return:` text has to carry the meaning that the
bare `Any` does not, so it explains that the type is whatever the convertor produced.

Two things to know about the docstrings themselves, both of which used to pass unnoticed and
now fail the build:

* Everything in a docstring must be indented consistently. A line at column 0 defeats the
  dedent and leaves every *other* line looking over-indented to docutils.
* The body of a `:param:` that wraps to a second line must be indented past the field marker.

`sphinx-autodoc-typehints` is pinned to a compatible release for the same reason Sphinx is:
the build runs with `-W`, so a release that reports forward references differently would break
the docs without a commit here.

This rule is about the library. `cooked_input/examples/` is exempt from `ANN`, so a type in one
of those docstrings is the only type information there is — leave it alone.

### Faking console input

`cooked_input` reads from the console, so nearly every test needs a fake keyboard. Use the
`fake_input` fixture from `cooked_input/tests/conftest.py` — it is the only supported way:

```python
def test_retries_past_a_bad_value(fake_input):
    feeder = fake_input("foo", "42")
    assert get_int() == 42
    assert feeder.remaining == 0
```

Multi-line strings are split into one response per line. The fixture patches both
`builtins.input` and `getpass.getpass`, so `hidden=True` prompts are covered too — patching
`sys.stdin` alone is not enough, because `getpass` ignores it whenever it can open `/dev/tty`.

When the script runs out the feeder raises `EOFError`. That is deliberate: a retry loop or a
`Table.run()` menu loop that would otherwise spin forever ends the test immediately instead of
hanging the run. Asserting `feeder.remaining == 0` afterwards proves the code asked for exactly
the inputs you scripted.

## Keeping the READMEs in sync

There are three README files, deliberately, because three places render them and
they do not accept the same format:

| File | Rendered by | Format |
| --- | --- | --- |
| `README.rst` | **PyPI** — `pyproject.toml` ships it as the long description | reStructuredText |
| `README.md` | **GitHub** — it is preferred over `README.rst` on the repo front page | Markdown |
| `docs/README.rst` | **Read the Docs** — it is the first page in the Sphinx toctree | reStructuredText |

`README.rst` is the canonical copy. A change to it belongs in `README.md` as well;
the two should stay word-for-word equivalent apart from markup. `docs/README.rst` is
a longer variant with its own intro wording and a Change log section, so it does not
need to match line for line — but the facts in it do.

The line that drifts in practice is the supported Python version. When it changes,
update **all four** of these together:

- `README.rst` — "tested through Python X.Y"
- `README.md` — same line
- `docs/README.rst` — "(tested through Python X.Y)"
- `pyproject.toml` — the `Programming Language :: Python :: X.Y` classifier, plus
  `tox.ini` envlist and the CI matrix in `.github/workflows/tests.yml`

This is exactly what went stale once already: `README.md` sat at 3.13 after the
other files moved to 3.14.
