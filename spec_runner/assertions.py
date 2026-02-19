import json
import inspect
from pathlib import Path
from typing import Any, Callable, Mapping

from spec_runner.internal_model import GroupNode, InternalAssertNode, PredicateLeaf
from spec_runner.spec_lang import SpecLangLimits, eval_predicate

def parse_json(text: str) -> Any:
    return json.loads(text)


def first_nonempty_line(text: str) -> str:
    for ln in (text or "").splitlines():
        if ln.strip():
            return ln.strip()
    return ""


def assert_stdout_path_exists(stdout: str, *, suffix: str | None = None) -> Path:
    line = first_nonempty_line(stdout)
    p = Path(line)
    assert line, "expected stdout to contain a path"
    assert p.exists(), f"expected path to exist: {p}"
    if suffix:
        assert p.name.endswith(str(suffix))
    return p


def _raise_with_assert_context(
    exc: BaseException,
    *,
    case_id: str,
    assert_path: str,
    target: str | None = None,
    op: str | None = None,
) -> None:
    ctx = f"[case_id={case_id} contract_path={assert_path}"
    if target is not None:
        ctx += f" target={target}"
    if op is not None:
        ctx += f" op={op}"
    ctx += "]"
    detail = str(exc).strip()
    msg = ctx if not detail else f"{ctx} {detail}"
    if isinstance(exc, AssertionError):
        raise AssertionError(msg) from exc
    if isinstance(exc, TypeError):
        raise TypeError(msg) from exc
    if isinstance(exc, ValueError):
        raise ValueError(msg) from exc
    raise RuntimeError(msg) from exc


def iter_leaf_assertions(leaf: Any, *, target_override: str | None = None):
    """
    Yield (target, op, value, is_true) tuples from a leaf assertion mapping.

    Canonical leaf shape:

    - target: stderr
      evaluate:
        - contains: [{var: subject}, "WARN:"]

    Rules:
    - leaf assertions MUST NOT define `target`; target is inherited from a
      parent group (`MUST` / `MAY` / `MUST_NOT`).
    - Each op key's value MUST be a list.
    - Duplicate keys are not allowed by YAML; multi-checks use lists.
    """
    if not isinstance(leaf, dict):
        raise TypeError("contract leaf must be a mapping")
    if "target" in leaf:
        raise ValueError("leaf contract predicate must not include key: target; move target to a parent group")
    target = str(target_override or "").strip()
    if not target:
        raise ValueError("contract leaf requires inherited target from a parent group")
    if any(k in leaf for k in ("MUST", "MAY", "MUST_NOT")):
        raise ValueError("leaf contract predicate must not include group keys")
    if not leaf:
        raise ValueError("contract leaf must be a non-empty expression mapping")
    if "evaluate" in leaf:
        raise ValueError("contract leaf must not use evaluate wrapper; place operator mapping directly in asserts")
    yield target, "evaluate", leaf, True


def eval_assert_tree(assert_spec: Any, *, eval_leaf) -> None:
    """
    Evaluate an assertion tree.

    Supported shapes:
    - list: implicit AND across items (top-level `contract:` is typically a list)
    - mapping with exactly one group key:
      - `MUST:`: AND across child nodes
      - `MAY:`: OR across child nodes (at least one must pass)
      - `MUST_NOT:`: NONE across child nodes (no child may pass)
    - group nodes may include `target:`; child leaves inherit that target
    - leaf mapping with op keys (target inherited from parent group)
    """

    leaf_sig = inspect.signature(eval_leaf)
    accepts_kwargs = "**" in str(leaf_sig)
    accepts_inherited_target = "inherited_target" in leaf_sig.parameters or accepts_kwargs
    accepts_assert_path = "assert_path" in leaf_sig.parameters or accepts_kwargs

    def _call_leaf(node: dict, *, inherited_target: str | None, assert_path: str) -> None:
        kwargs = {}
        if accepts_inherited_target:
            kwargs["inherited_target"] = inherited_target
        if accepts_assert_path:
            kwargs["assert_path"] = assert_path
        if kwargs:
            eval_leaf(node, **kwargs)
        else:
            eval_leaf(node)

    def _eval_node(node: Any, *, inherited_target: str | None = None, path: str = "contract") -> None:
        if node is None:
            return
        if isinstance(node, list):
            for idx, child in enumerate(node):
                _eval_node(child, inherited_target=inherited_target, path=f"{path}[{idx}]")
            return
        if not isinstance(node, dict):
            raise TypeError("contract node must be a mapping or a list")
        step_class = str(node.get("class", "")).strip() if "class" in node else ""
        if step_class in {"MUST", "MAY", "MUST_NOT"} and "asserts" in node:
            step_id = str(node.get("id", "")).strip()
            if not step_id:
                raise ValueError(f"{path}.id must be a non-empty string")
            extra = [k for k in node.keys() if k not in ("id", "class", "target", "asserts")]
            if extra:
                bad = sorted(str(k) for k in extra)[0]
                raise ValueError(f"unknown key in contract step: {bad}")
            node_target = str(node.get("target", "")).strip() or inherited_target
            children = node.get("asserts")
            if not isinstance(children, list):
                raise TypeError("contract step asserts must be a list")
            if not children:
                raise ValueError("contract step asserts must not be empty")
            step_path = path
            if step_class == "MUST":
                for idx, child in enumerate(children):
                    _eval_node(child, inherited_target=node_target, path=f"{step_path}.asserts[{idx}]")
                return
            if step_class == "MAY":
                failures: list[BaseException] = []
                any_passed = False
                for idx, child in enumerate(children):
                    try:
                        _eval_node(child, inherited_target=node_target, path=f"{step_path}.asserts[{idx}]")
                        any_passed = True
                        break
                    except AssertionError as e:
                        failures.append(e)
                if not any_passed:
                    msg = "all 'MAY' branches failed"
                    if failures:
                        details = "\n".join(f"- {str(e) or e.__class__.__name__}" for e in failures[:5])
                        msg = f"{msg}:\n{details}"
                    raise AssertionError(msg)
                return
            if step_class == "MUST_NOT":
                passed = 0
                for idx, child in enumerate(children):
                    try:
                        _eval_node(child, inherited_target=node_target, path=f"{step_path}.asserts[{idx}]")
                        passed += 1
                    except AssertionError:
                        continue
                if passed:
                    raise AssertionError(f"'MUST_NOT' failed: {passed} branch(es) passed")
                return

        present_groups = [k for k in ("MUST", "MAY", "MUST_NOT") if k in node]
        if present_groups:
            if len(present_groups) > 1:
                keys = ", ".join(present_groups)
                raise ValueError(f"contract group must include exactly one key (MUST/MAY/MUST_NOT), got: {keys}")
            node_target = str(node.get("target", "")).strip() or inherited_target
            group_key = present_groups[0]
            extra = [k for k in node.keys() if k not in (group_key, "target")]
            if extra:
                bad = sorted(str(k) for k in extra)[0]
                raise ValueError(f"unknown key in contract group: {bad}")

            if group_key == "MUST":
                children = node.get("MUST")
                if not isinstance(children, list):
                    raise TypeError("contract.MUST must be a list")
                if not children:
                    raise ValueError("contract.MUST must not be empty")
                for idx, child in enumerate(children):
                    _eval_node(child, inherited_target=node_target, path=f"{path}.MUST[{idx}]")

            if group_key == "MAY":
                children = node.get("MAY")
                if not isinstance(children, list):
                    raise TypeError("contract.MAY must be a list")
                if not children:
                    raise ValueError("contract.MAY must not be empty")
                # MAY: pass if at least one child passes; if all fail, raise a helpful message.
                group_failures: list[BaseException] = []
                any_passed = False
                for idx, child in enumerate(children):
                    try:
                        _eval_node(child, inherited_target=node_target, path=f"{path}.MAY[{idx}]")
                        any_passed = True
                        break
                    except AssertionError as e:
                        group_failures.append(e)
                if not any_passed:
                    msg = "all 'MAY' branches failed"
                    if group_failures:
                        details = "\n".join(
                            f"- {str(e) or e.__class__.__name__}" for e in group_failures[:5]
                        )
                        msg = f"{msg}:\n{details}"
                    raise AssertionError(msg)

            if group_key == "MUST_NOT":
                children = node.get("MUST_NOT")
                if not isinstance(children, list):
                    raise TypeError("contract.MUST_NOT must be a list")
                if not children:
                    raise ValueError("contract.MUST_NOT must not be empty")
                # MUST_NOT: pass only when every child assertion fails.
                passed = 0
                for idx, child in enumerate(children):
                    try:
                        _eval_node(child, inherited_target=node_target, path=f"{path}.MUST_NOT[{idx}]")
                        passed += 1
                    except AssertionError:
                        continue
                if passed:
                    raise AssertionError(f"'MUST_NOT' failed: {passed} branch(es) passed")

            return

        # Leaf
        _call_leaf(node, inherited_target=inherited_target, assert_path=path)

    _eval_node(assert_spec)


def evaluate_internal_assert_tree(
    assert_tree: InternalAssertNode,
    *,
    case_id: str,
    subject_for_key: Callable[[str], Any],
    limits: SpecLangLimits,
    symbols: Mapping[str, Any] | None = None,
    imports: Mapping[str, str] | None = None,
    capabilities: set[str] | frozenset[str] | None = None,
    on_clause_pass: Callable[[dict[str, Any], dict[str, int]], None] | None = None,
    on_clause_fail: Callable[[dict[str, Any], BaseException, dict[str, int]], None] | None = None,
    on_complete: Callable[[dict[str, int]], None] | None = None,
) -> None:
    """
    Evaluate compiled internal contract tree nodes.

    Harnesses provide target -> subject resolution; all predicate checks run
    through spec-lang expressions.
    """

    def _eval_node(node: InternalAssertNode) -> None:
        if isinstance(node, PredicateLeaf):
            try:
                leaf_symbols: dict[str, Any] = dict(symbols or {})
                for name, spec in (node.imports or {}).items():
                    src = str(spec.get("from", "")).strip()
                    if src == "artifact":
                        key = str(spec.get("key", "")).strip()
                        if not key:
                            raise ValueError(f"{node.assert_path}: imports.{name}.key must be non-empty")
                        leaf_symbols[name] = subject_for_key(key)
                    elif src == "symbol":
                        key = str(spec.get("key", "")).strip()
                        if not key:
                            raise ValueError(f"{node.assert_path}: imports.{name}.key must be non-empty")
                        if key not in leaf_symbols:
                            raise ValueError(f"{node.assert_path}: imports.{name} unknown symbol key: {key}")
                        leaf_symbols[name] = leaf_symbols[key]
                    elif src == "literal":
                        leaf_symbols[name] = spec.get("value")
                    else:
                        raise ValueError(f"{node.assert_path}: imports.{name}.from invalid: {src}")
                subject = leaf_symbols.get("subject")
                ok = eval_predicate(
                    node.expr,
                    subject=subject,
                    limits=limits,
                    symbols=leaf_symbols,
                    imports=imports,
                    capabilities=capabilities,
                )
                assert ok, "evaluate contract failed"
            except BaseException as e:  # noqa: BLE001
                _raise_with_assert_context(
                    e,
                    case_id=case_id,
                    assert_path=node.assert_path,
                    target=node.target,
                    op=node.op,
                )
            return

        if not isinstance(node, GroupNode):
            raise TypeError("internal contract node must be GroupNode or PredicateLeaf")

        if node.op == "MUST":
            for child in node.children:
                _eval_node(child)
            return

        if node.op == "MAY":
            failures: list[BaseException] = []
            for child in node.children:
                try:
                    _eval_node(child)
                    return
                except AssertionError as e:
                    failures.append(e)
            msg = "all 'MAY' branches failed"
            if failures:
                details = "\n".join(f"- {str(e) or e.__class__.__name__}" for e in failures[:5])
                msg = f"{msg}:\n{details}"
            raise AssertionError(msg)

        if node.op == "MUST_NOT":
            passed = 0
            for child in node.children:
                try:
                    _eval_node(child)
                    passed += 1
                except AssertionError:
                    continue
            if passed:
                raise AssertionError(f"'MUST_NOT' failed: {passed} branch(es) passed")
            return

        raise ValueError(f"unknown internal contract group op: {node.op}")

    def _clause_from_node(node: InternalAssertNode, *, index: int) -> dict[str, Any]:
        if isinstance(node, GroupNode):
            class_name = node.op
            target = node.target
            assert_path = node.assert_path
        else:
            class_name = "MUST"
            target = node.target
            assert_path = node.assert_path
        clause_id: str | None = None
        if "<" in assert_path and assert_path.endswith(">"):
            clause_id = assert_path.rsplit("<", 1)[-1].rstrip(">").strip() or None
        return {
            "index": int(index),
            "id": clause_id,
            "class": class_name,
            "assert_path": assert_path,
            "target": target,
        }

    totals: dict[str, int] = {
        "passed_clauses": 0,
        "failed_clauses": 0,
        "MUST_passed": 0,
        "MAY_passed": 0,
        "MUST_NOT_passed": 0,
    }
    if isinstance(assert_tree, GroupNode) and assert_tree.op == "MUST":
        clauses: list[InternalAssertNode] = list(assert_tree.children)
    else:
        clauses = [assert_tree]

    for idx, clause in enumerate(clauses):
        clause_ctx = _clause_from_node(clause, index=idx)
        try:
            _eval_node(clause)
            totals["passed_clauses"] += 1
            class_key = f"{clause_ctx['class']}_passed"
            if class_key in totals:
                totals[class_key] += 1
            if on_clause_pass is not None:
                on_clause_pass(clause_ctx, dict(totals))
        except BaseException as exc:  # noqa: BLE001
            totals["failed_clauses"] += 1
            if on_clause_fail is not None:
                on_clause_fail(clause_ctx, exc, dict(totals))
            raise

    if on_complete is not None:
        on_complete(dict(totals))
