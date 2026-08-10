#!/usr/bin/env python3
"""Fail if the project disagrees with itself about which Pythons it supports.

The supported Python range is stated in six places, and they drift: README.md sat at
"tested through Python 3.13" for a while after everything else moved to 3.14. This
script is the executable form of the "Keeping the READMEs in sync" section of
CONTRIBUTING.md.

Run it from the repository root:

    python scripts/check_version_claims.py

Exits 0 when every source agrees, 1 otherwise, printing what each source claims.
"""

from __future__ import annotations

import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# "3.9" must sort below "3.10", so compare on the parsed tuple rather than the string.
Version = tuple[int, int]


@dataclass(frozen=True)
class Claim:
    """What one file says the supported Python range is."""

    source: str
    floor: Version | None
    ceiling: Version | None


def _parse(version: str) -> Version:
    major, minor = version.split(".")
    return int(major), int(minor)


def _show(version: Version | None) -> str:
    return f"{version[0]}.{version[1]}" if version else "-"


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def claim_from_prose(relative_path: str) -> Claim:
    """Read the floor and ceiling out of a README's prose.

    Both root READMEs say "requires Python X.Y or later ... tested through Python A.B";
    docs/README.rst says "Python X.Y or later (tested through Python A.B)".
    """
    text = _read(relative_path)
    floor = re.search(r"Python (\d+\.\d+) or later", text)
    ceiling = re.search(r"tested through Python (\d+\.\d+)", text)
    return Claim(
        source=relative_path,
        floor=_parse(floor.group(1)) if floor else None,
        ceiling=_parse(ceiling.group(1)) if ceiling else None,
    )


def claim_from_pyproject() -> Claim:
    """Floor from requires-python, ceiling from the highest version classifier."""
    data = tomllib.loads(_read("pyproject.toml"))
    project = data["project"]

    requires = re.search(r"(\d+\.\d+)", project["requires-python"])
    # "Programming Language :: Python :: 3" and ":: 3 :: Only" carry no minor version.
    minors = [
        _parse(match.group(1))
        for classifier in project["classifiers"]
        if (match := re.fullmatch(r"Programming Language :: Python :: (\d+\.\d+)", classifier))
    ]
    return Claim(
        source="pyproject.toml",
        floor=_parse(requires.group(1)) if requires else None,
        ceiling=max(minors) if minors else None,
    )


def claim_from_envlist(relative_path: str, token: str, on_lines_with: str | None = None) -> Claim:
    """Floor and ceiling from a list of version tokens.

    When ``on_lines_with`` is given, only lines containing that substring are searched,
    and every token on such a line counts. That matters for the CI matrix, where one
    line holds the whole list: `python-version: ["3.10", "3.11", "3.12", ...]`. Scanning
    the file as a whole would match only the first entry of that list.
    """
    text = _read(relative_path)
    lines = (
        [line for line in text.splitlines() if on_lines_with in line]
        if on_lines_with is not None
        else [text]
    )
    found = [_parse(f"{m[0]}.{m[1]}") for line in lines for m in re.findall(token, line)]
    return Claim(
        source=relative_path,
        floor=min(found) if found else None,
        ceiling=max(found) if found else None,
    )


def collect_claims() -> list[Claim]:
    return [
        claim_from_prose("README.rst"),
        claim_from_prose("README.md"),
        claim_from_prose("docs/README.rst"),
        claim_from_pyproject(),
        # tox.ini: "envlist = py310,py311,..." -> py(3)(10)
        claim_from_envlist("tox.ini", r"\bpy(3)(\d\d)\b"),
        # tests.yml: every quoted "3.NN" on a python-version line. The ${{ matrix... }}
        # reference on the setup-python step carries no literal version, so it is ignored.
        claim_from_envlist(
            ".github/workflows/tests.yml", r'"(3)\.(\d+)"', on_lines_with="python-version"
        ),
    ]


def main() -> int:
    claims = collect_claims()

    for claim in claims:
        print(f"  {claim.source:32s} floor={_show(claim.floor):6s} ceiling={_show(claim.ceiling)}")

    problems: list[str] = []

    missing = [c.source for c in claims if c.floor is None or c.ceiling is None]
    if missing:
        problems.append(
            "could not find a version claim in: "
            + ", ".join(missing)
            + " (did the wording change? update scripts/check_version_claims.py)"
        )

    for field in ("floor", "ceiling"):
        values = {getattr(c, field) for c in claims if getattr(c, field) is not None}
        if len(values) > 1:
            detail = ", ".join(
                f"{c.source}={_show(getattr(c, field))}"
                for c in claims
                if getattr(c, field) is not None
            )
            problems.append(f"{field} disagrees across sources: {detail}")

    if problems:
        print("\nFAIL: the project disagrees with itself about supported Pythons.\n")
        for problem in problems:
            print(f"  - {problem}")
        print("\nSee the 'Keeping the READMEs in sync' section of CONTRIBUTING.md.")
        return 1

    supported = claims[0]
    print(f"\nOK: every source agrees on {_show(supported.floor)} through {_show(supported.ceiling)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
