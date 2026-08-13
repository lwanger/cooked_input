"""Check every keyword argument written anywhere in this repo against the real signature.

Two shipped defects had the same shape: a keyword that matched no parameter. #82 passed
``show_border`` and ``show_cols`` to :class:`Table`, which has neither -- they are
:class:`TableStyle` fields. #84 passed ``elem_validators`` to ``get_list``, which has never
had it. Both were swallowed by the old ``**options`` bag, both changed what the demo did
while it claimed otherwise, and both were found by hand.

``ty`` now covers the package and the examples (issue #85), but it will never read the
``.. code-block:: python`` snippets in ``docs/``, which are the code users copy first. This
walks the source *and* the docs and checks each keyword against the signature it targets.

The audit is deliberately conservative, because a false positive here would make the whole
test worthless -- someone would mark it xfail and the real finding would go with it. It
gives up silently on anything it cannot resolve unambiguously:

* only calls naming a public ``cooked_input`` callable are checked;
* a name defined in the same module shadows the package's, so it is skipped;
* a signature taking ``**kwargs`` accepts anything, so it is skipped;
* a method call is checked only when that method name belongs to exactly one public class;
* a snippet that will not parse is skipped rather than failed.

Len Wanger, 2026
"""

from __future__ import annotations

import ast
import inspect
from collections.abc import Iterator
from pathlib import Path
from typing import Any, NamedTuple

import pytest

import cooked_input as ci

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Directories whose .py files are audited, and the docs whose code blocks are.
PYTHON_ROOTS = ("cooked_input", "cooked_input/tests", "cooked_input/examples")
DOCS_ROOT = "docs"


class Finding(NamedTuple):
    """One keyword that the callee does not accept."""

    origin: str
    line: int
    call: str
    keyword: str
    accepted: tuple[str, ...]

    def __str__(self) -> str:
        return (f"{self.origin}:{self.line}: {self.call}() has no parameter "
                f"{self.keyword!r} (accepts: {', '.join(self.accepted)})")


def _public_callables() -> dict[str, Any]:
    """Map every public ``cooked_input`` name to the function or class it names."""
    targets: dict[str, Any] = {}
    for name in dir(ci):
        if name.startswith("_"):
            continue
        target = getattr(ci, name)
        if inspect.isfunction(target) or inspect.isclass(target):
            targets[name] = target
    return targets


def _unique_methods() -> dict[str, Any]:
    """Map method names owned by exactly one public class to that method.

    A name on two classes is dropped: ``tbl.foo(...)`` gives no way to tell which one is
    meant, and guessing is how a checker like this starts crying wolf.
    """
    owners: dict[str, Any] = {}
    ambiguous: set[str] = set()

    for target in _public_callables().values():
        if not inspect.isclass(target):
            continue
        for name, method in inspect.getmembers(target, inspect.isfunction):
            if name.startswith("_"):
                continue
            if name in owners and owners[name] is not method:
                ambiguous.add(name)
            owners[name] = method

    return {name: method for name, method in owners.items() if name not in ambiguous}


TARGETS = _public_callables()
METHODS = _unique_methods()


def _accepted_keywords(target: Any) -> set[str] | None:
    """Return the keyword names ``target`` accepts, or **None** if it accepts anything."""
    try:
        signature = inspect.signature(target)
    except (TypeError, ValueError):
        return None

    accepted: set[str] = set()
    for parameter in signature.parameters.values():
        if parameter.kind is inspect.Parameter.VAR_KEYWORD:
            return None
        if parameter.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                              inspect.Parameter.KEYWORD_ONLY):
            accepted.add(parameter.name)
    return accepted


def _module_aliases(tree: ast.AST) -> set[str]:
    """Names this module can reach ``cooked_input`` through -- usually ``ci``."""
    aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if name.name == "cooked_input":
                    aliases.add(name.asname or name.name)
    return aliases


def _shadowed_names(tree: ast.AST) -> set[str]:
    """Names this module defines itself, which therefore are not the package's."""
    return {node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def _raises_type_error(expr: ast.expr) -> bool:
    """Is this the ``pytest.raises(TypeError)`` context manager?"""
    if not isinstance(expr, ast.Call) or not expr.args:
        return False

    called = expr.func.attr if isinstance(expr.func, ast.Attribute) else getattr(expr.func, "id", "")
    if called != "raises":
        return False

    first = expr.args[0]
    expected = first.elts if isinstance(first, ast.Tuple) else [first]
    return any(isinstance(node, ast.Name) and node.id == "TypeError" for node in expected)


def _deliberate_calls(tree: ast.AST) -> set[int]:
    """Calls inside a ``with pytest.raises(TypeError)`` block, by node id.

    This suite asserts that a misspelled option is rejected -- ``ci.get_int(promt=...)`` and
    friends. There the bad keyword *is* the assertion, so flagging it would make the audit
    fail on the very tests that prove the behaviour it cares about. Only ``TypeError`` earns
    the exemption: a bad keyword under ``pytest.raises(ValueError)`` is still a defect.
    """
    deliberate: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.With, ast.AsyncWith)):
            continue
        if not any(_raises_type_error(item.context_expr) for item in node.items):
            continue
        for descendant in ast.walk(node):
            if isinstance(descendant, ast.Call):
                deliberate.add(id(descendant))
    return deliberate


def _resolve(func: ast.expr, aliases: set[str], shadowed: set[str]) -> tuple[Any, str] | None:
    """Work out what is being called, or **None** when that cannot be settled."""
    if isinstance(func, ast.Name):
        if func.id in shadowed or func.id not in TARGETS:
            return None
        return TARGETS[func.id], func.id

    if isinstance(func, ast.Attribute):
        # ci.get_string(...) -- unambiguous, the alias names the package.
        if isinstance(func.value, ast.Name) and func.value.id in aliases:
            if func.attr in TARGETS:
                return TARGETS[func.attr], f"{func.value.id}.{func.attr}"
            return None

        # tbl.get_table_choice(...) -- only when one public class owns that name.
        if func.attr in METHODS:
            return METHODS[func.attr], f".{func.attr}"

    return None


def audit_tree(tree: ast.AST, origin: str, line_offset: int = 0,
               aliases: set[str] | None = None, shadowed: set[str] | None = None) -> list[Finding]:
    """Report every keyword in ``tree`` that its callee does not accept.

    ``aliases`` and ``shadowed`` are normally read from the tree itself. They are passed in
    only by the line-by-line salvage in :func:`audit_snippet`, where each line is its own
    tree and the ``import cooked_input as ci`` sits in a different one.
    """
    aliases = _module_aliases(tree) if aliases is None else aliases
    shadowed = _shadowed_names(tree) if shadowed is None else shadowed
    deliberate = _deliberate_calls(tree)
    findings: list[Finding] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.keywords:
            continue
        if id(node) in deliberate:
            continue

        resolved = _resolve(node.func, aliases, shadowed)
        if resolved is None:
            continue

        target, label = resolved
        accepted = _accepted_keywords(target)
        if accepted is None:
            continue

        for keyword in node.keywords:
            if keyword.arg is None:  # **splat at the call site -- nothing to check
                continue
            if keyword.arg not in accepted:
                findings.append(Finding(origin, node.lineno + line_offset, label,
                                        keyword.arg, tuple(sorted(accepted))))

    return findings


def audit_source(source: str, origin: str) -> list[Finding]:
    """Audit one Python source string."""
    return audit_tree(ast.parse(source), origin)


def _strip_prompts(source: str) -> str:
    """Drop the ``>>>`` and ``...`` prompts a doctest-style block carries."""
    lines = []
    for line in source.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(">>> ") or stripped.startswith("... "):
            lines.append(stripped[4:])
        elif stripped in (">>>", "..."):
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines)


def _snippet_trees(source: str) -> list[tuple[int, ast.AST]]:
    """Parse a doc snippet, salvaging whatever will parse.

    Doc blocks are not always valid Python: ``docs/tutorial2.rst`` interleaves ``>>>``
    prompts with the table art the call prints. The whole block is tried first, then the
    same with prompts stripped, and finally line by line -- which keeps the one real call
    in a block whose remaining lines are output. Anything that still will not parse is
    dropped, never failed.

    Returns:
        ``(line offset within the snippet, tree)`` pairs.
    """
    for candidate in (source, _strip_prompts(source)):
        try:
            return [(0, ast.parse(candidate))]
        except SyntaxError:
            continue

    trees: list[tuple[int, ast.AST]] = []
    for offset, line in enumerate(_strip_prompts(source).splitlines()):
        try:
            trees.append((offset, ast.parse(line.strip())))
        except SyntaxError:
            continue
    return trees


def audit_snippet(source: str, origin: str, first_line: int,
                  aliases: set[str] | None = None,
                  shadowed: set[str] | None = None) -> list[Finding]:
    """Audit one documentation snippet."""
    trees = _snippet_trees(source)

    if aliases is None or shadowed is None:
        found_aliases, found_shadowed = _names_in(trees)
        aliases = found_aliases if aliases is None else aliases
        shadowed = found_shadowed if shadowed is None else shadowed

    findings: list[Finding] = []
    for offset, tree in trees:
        findings.extend(audit_tree(tree, origin, line_offset=first_line + offset - 1,
                                   aliases=aliases, shadowed=shadowed))
    return findings


def _names_in(trees: list[tuple[int, ast.AST]]) -> tuple[set[str], set[str]]:
    """The package aliases and the locally defined names across a group of trees."""
    aliases: set[str] = set()
    shadowed: set[str] = set()
    for _, tree in trees:
        aliases |= _module_aliases(tree)
        shadowed |= _shadowed_names(tree)
    return aliases, shadowed


def audit_document(text: str, origin: str) -> list[Finding]:
    """Audit every code block in one rst file.

    Aliases are collected across the whole document before anything is judged. A doc
    imports ``cooked_input as ci`` once near the top and then writes ``ci.get_string(...)``
    in every block after it -- ``docs/quick_start.rst`` does exactly that -- so resolving
    per block would have found almost nothing.
    """
    blocks = list(_code_blocks(text))
    aliases, shadowed = _names_in([(0, tree) for _, block in blocks
                                   for _, tree in _snippet_trees(block)])

    findings: list[Finding] = []
    for first_line, block in blocks:
        findings.extend(audit_snippet(block, origin, first_line, aliases, shadowed))
    return findings


def _code_blocks(text: str) -> Iterator[tuple[int, str]]:
    """Yield ``(first line number, dedented source)`` for each literal block in an rst file.

    Covers both the explicit ``.. code-block:: python`` directive and the bare ``::``
    literal block, since cooked_input's docs use each. Non-Python blocks are picked up
    too; they simply fail to parse later and are dropped.
    """
    lines = text.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index]
        opens_block = line.strip().startswith(".. code-block:: python") or line.rstrip().endswith("::")
        index += 1
        if not opens_block:
            continue

        while index < len(lines) and not lines[index].strip():
            index += 1
        if index >= len(lines):
            return

        first_line = index + 1
        indent = len(lines[index]) - len(lines[index].lstrip())
        block: list[str] = []
        while index < len(lines):
            current = lines[index]
            if current.strip() and (len(current) - len(current.lstrip())) < indent:
                break
            block.append(current[indent:] if current.strip() else "")
            index += 1

        if block:
            yield first_line, "\n".join(block)


def _python_files() -> list[Path]:
    """Every .py file the audit covers, without recursing past the listed roots."""
    files: list[Path] = []
    for root in PYTHON_ROOTS:
        files.extend(sorted((REPO_ROOT / root).glob("*.py")))
    return files


def _doc_files() -> list[Path]:
    return sorted((REPO_ROOT / DOCS_ROOT).glob("*.rst"))


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


PYTHON_FILES = _python_files()
DOC_FILES = _doc_files()


@pytest.mark.parametrize("path", PYTHON_FILES, ids=_relative)
def test_no_python_call_uses_an_unknown_keyword(path: Path) -> None:
    findings = audit_source(path.read_text(encoding="utf-8"), _relative(path))
    assert not findings, "\n".join(str(finding) for finding in findings)


@pytest.mark.parametrize("path", DOC_FILES, ids=_relative)
def test_no_documented_call_uses_an_unknown_keyword(path: Path) -> None:
    findings = audit_document(path.read_text(encoding="utf-8"), _relative(path))
    assert not findings, "\n".join(str(finding) for finding in findings)


class TestTheAuditIsNotVacuous:
    """A checker that silently resolves nothing would pass forever and prove nothing.

    Both halves need guarding: that it reaches real calls, and that it still bites when
    one of them is wrong.
    """

    def test_the_public_surface_was_discovered(self) -> None:
        assert "get_string" in TARGETS
        assert "Table" in TARGETS
        # get_table_choice lives only on Table, so method calls on it are resolvable.
        assert "get_table_choice" in METHODS

    def test_many_real_calls_are_resolved(self) -> None:
        """Counted across the repo, so a resolution regression shows up as a drop."""
        resolved = 0
        for path in PYTHON_FILES:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            aliases = _module_aliases(tree)
            shadowed = _shadowed_names(tree)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and node.keywords:
                    if _resolve(node.func, aliases, shadowed) is not None:
                        resolved += 1

        assert resolved > 100, f"only {resolved} keyword calls resolved -- audit is barely looking"

    def test_the_docs_half_reaches_real_calls(self) -> None:
        """The rst extraction is fiddly, and silently extracting nothing would look like a pass."""
        resolved = 0
        for path in DOC_FILES:
            blocks = list(_code_blocks(path.read_text(encoding="utf-8")))
            if not blocks:
                continue
            aliases, shadowed = _names_in([(0, tree) for _, block in blocks
                                           for _, tree in _snippet_trees(block)])
            for _, block in blocks:
                for _, tree in _snippet_trees(block):
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call) and node.keywords:
                            if _resolve(node.func, aliases, shadowed) is not None:
                                resolved += 1

        assert resolved > 40, f"only {resolved} documented keyword calls resolved"

    def test_a_bogus_keyword_on_a_function_is_caught(self) -> None:
        """The #84 shape: get_list never had elem_validators."""
        source = "import cooked_input as ci\nci.get_list(prompt='x', elem_validators=None)\n"
        findings = audit_source(source, "<synthetic>")

        assert len(findings) == 1
        assert findings[0].keyword == "elem_validators"

    def test_a_bogus_keyword_on_a_class_is_caught(self) -> None:
        """The #82 shape: show_border is a TableStyle field, not a Table option."""
        source = "from cooked_input import Table\nTable(rows=[], show_border=False)\n"
        findings = audit_source(source, "<synthetic>")

        assert [finding.keyword for finding in findings] == ["show_border"]

    def test_a_bogus_keyword_in_a_doc_block_is_caught(self) -> None:
        block = "import cooked_input as ci\nci.get_int(prompt='n', maximum_value=10)\n"
        findings = audit_snippet(block, "<synthetic.rst>", first_line=7)

        assert len(findings) == 1
        assert findings[0].keyword == "maximum_value"
        assert findings[0].line == 8

    def test_a_doctest_block_with_output_still_yields_its_call(self) -> None:
        """tutorial2.rst's shape -- a real call followed by the table it prints."""
        block = (">>> import cooked_input as ci\n"
                 ">>> v = ci.get_string(prompt='name', bogus_option=1)\n"
                 ">>> +-------------+\n"
                 ">>> |        name |\n")
        findings = audit_snippet(block, "<synthetic.rst>", first_line=1)

        assert [finding.keyword for finding in findings] == ["bogus_option"]


class TestTheAuditHoldsItsFire:
    """The skips that keep it from crying wolf."""

    def test_a_locally_defined_name_is_not_the_package_one(self) -> None:
        source = ("def get_string(**anything):\n"
                  "    pass\n"
                  "get_string(whatever=1)\n")
        assert audit_source(source, "<synthetic>") == []

    def test_a_signature_taking_kwargs_is_skipped(self) -> None:
        """Nothing can be said about a callee that accepts every keyword."""
        assert _accepted_keywords(lambda **kwargs: None) is None

    def test_an_unresolvable_method_call_is_skipped(self) -> None:
        source = "some_object.frobnicate(nonsense=1)\n"
        assert audit_source(source, "<synthetic>") == []

    def test_a_splatted_call_is_skipped(self) -> None:
        source = ("import cooked_input as ci\n"
                  "options = {'prompt': 'x'}\n"
                  "ci.get_string(**options)\n")
        assert audit_source(source, "<synthetic>") == []

    def test_an_unparseable_snippet_is_skipped(self) -> None:
        assert audit_snippet("+---+---+\n| not python |\n", "<synthetic.rst>", 1) == []

    def test_a_bad_keyword_asserted_with_pytest_raises_is_skipped(self) -> None:
        """This suite's own "an unknown option is rejected" tests must not trip the audit."""
        source = ("import cooked_input as ci\n"
                  "with pytest.raises(TypeError, match='promt'):\n"
                  "    ci.get_int(promt='How old are you?')\n")
        assert audit_source(source, "<synthetic>") == []

    def test_only_type_error_earns_that_exemption(self) -> None:
        """A bad keyword under any other expected exception is still a defect."""
        source = ("import cooked_input as ci\n"
                  "with pytest.raises(ValueError):\n"
                  "    ci.get_int(promt='How old are you?')\n")
        findings = audit_source(source, "<synthetic>")

        assert [finding.keyword for finding in findings] == ["promt"]
