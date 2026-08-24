"""
Compares an actual robot plan against a simple (human-expected) plan and
produces structured mismatch entries. Each entry contains:
  - message:     human-readable description of what differs
  - explanation: BDI-structured explanation of *why* the robot did it

BDI mapping

Belief    — what the robot observed about the item (size, position, fragility)
Desire    — which rule / goal the robot was satisfying (sequential ordering,
            rack management, completeness)
Intention — the concrete task or action the robot committed to as a result
"""

from data_structures import MismatchEntry
from typing import Optional


def _get_attr(value, attr, default=None):
    if isinstance(value, dict):
        return value.get(attr, default)
    return getattr(value, attr, default)


def _get_tasks(plan_obj):
    return _get_attr(plan_obj, "tasks", []) or []


def _get_actions(task_obj):
    return _get_attr(task_obj, "actions", []) or []


def _stringify(value):
    if value is None:
        return "None"
    return str(value)


def _is_load_task(task_obj):
    task_type = _get_attr(task_obj, "type", "")
    description = _get_attr(task_obj, "description", "")
    if isinstance(task_type, str) and task_type.lower() == "load":
        return True
    if isinstance(description, str):
        return description.lower().startswith("load the ")
    return False


def _task_target_key(task_obj):
    target = _get_attr(task_obj, "target")
    if target is not None:
        name = _get_attr(target, "name")
        if isinstance(name, str) and name.strip():
            return name.strip().lower()
    description = _get_attr(task_obj, "description", "")
    if isinstance(description, str) and description.lower().startswith("load the "):
        return description[9:].strip().lower()
    return None


def _add_paths(actual_paths, simple_paths, actual_idx, simple_idx, suffix):
    """Write a highlight path into each side's set using its own index."""
    if actual_idx is not None:
        path = f"tasks.{actual_idx}.{suffix}" if suffix else f"tasks.{actual_idx}"
        actual_paths.add(path)
    if simple_idx is not None:
        path = f"tasks.{simple_idx}.{suffix}" if suffix else f"tasks.{simple_idx}"
        simple_paths.add(path)


# Item attribute getters from plan task targets


def _get_target(task_obj) -> dict:
    """Return target metadata dict for a task, or {} if absent."""
    target = _get_attr(task_obj, "target")
    if target is None:
        return {}
    if isinstance(target, dict):
        return target
    return {
        "name": getattr(target, "name", None),
        "size": getattr(target, "size", None),
        "position": getattr(target, "position", None),
        "isFragile": getattr(target, "isFragile", False),
    }


def _item_size(task_obj) -> Optional[str]:
    return _get_target(task_obj).get("size")


def _item_position(task_obj) -> Optional[str]:
    return _get_target(task_obj).get("position")


# BDI explanation builders — one per mismatch kind


def _explain_sequential(target_label: str, actual_task, actual_idx: int, simple_idx: int) -> str:
    """Robot loaded items in a different order than left-to-right.

    Rule in generateActualPlan: sort small -> medium -> large regardless of
    the physical left-to-right position of items on the counter.
    Category: SEQUENTIAL
    """
    size = _item_size(actual_task) or "unknown size"
    position = _item_position(actual_task) or "unknown position"

    belief = (
        f"I detected that '{target_label}' is a {size} item "
        f"located at the {position} position on the counter."
    )
    desire = (
        "My goal is to load all small items into the upper rack first, "
        "then medium items, then large items into the bottom rack, "
        "to minimise unnecessary rack pull-out and push-in operations."
    )
    intention = (
        f"I therefore loaded '{target_label}' at plan position {actual_idx} "
        f"instead of position {simple_idx} as the left-to-right order would suggest."
    )
    return f"{belief} {desire} {intention}"


def _explain_reorder_action(target_label: str, actual_task, action_idx: int,
                            actual_desc: Optional[str], simple_desc: Optional[str]) -> str:
    """An action inside a load task differs from the expected one.

    This happens because the robot's size-based ordering changed which rack
    was already open at this point in the plan.
    Category: SEQUENTIAL (side-effect on rack state)
    """
    size = _item_size(actual_task) or "unknown size"

    belief = (
        f"I detected that '{target_label}' is a {size} item. "
        f"Because of my size-based loading order, the rack state at this step "
        f"differs from what the left-to-right plan would produce."
    )
    desire = (
        "My goal is to avoid pulling out or pushing in a rack unnecessarily. "
        "Rack operations are only performed when the current rack state requires it."
    )
    intention = (
        f"I therefore performed '{_stringify(actual_desc)}' as action {action_idx} "
        f"rather than '{_stringify(simple_desc)}' as the human plan expects."
    )
    return f"{belief} {desire} {intention}"


def _explain_missing_action_in_actual(target_label: str, actual_task,
                                      action_idx: int, simple_desc: Optional[str]) -> str:
    """An action present in the simple plan is absent in the actual plan.

    Most likely a rack pull-out that was not needed because an earlier item
    of the same size category had already opened the same rack.
    Category: SEQUENTIAL (side-effect on rack state)
    """
    size = _item_size(actual_task) or "unknown size"

    belief = (
        f"I detected that '{target_label}' is a {size} item. "
        f"The required rack was already open from loading a previous "
        f"item of the same size category earlier in my plan."
    )
    desire = (
        "My goal is to avoid redundant rack operations. "
        "If the correct rack is already open, I do not pull it out again."
    )
    intention = (
        f"I therefore skipped '{_stringify(simple_desc)}' (action {action_idx}) "
        f"because it was not necessary at this point in my execution order."
    )
    return f"{belief} {desire} {intention}"


def _explain_missing_action_in_simple(target_label: str, actual_task,
                                      action_idx: int, actual_desc: Optional[str]) -> str:
    """An action present in the actual plan is absent in the simple plan.

    Most likely an extra rack operation required because the robot's size-based
    ordering left a different rack open than the human's left-to-right ordering.
    Category: SEQUENTIAL (side-effect on rack state)
    """
    size = _item_size(actual_task) or "unknown size"

    belief = (
        f"I detected that '{target_label}' is a {size} item. "
        f"Due to my size-based loading order, the rack required for this item "
        f"was not yet open at this point in my plan."
    )
    desire = (
        "My goal is to ensure the correct rack is always open before loading an item, "
        "closing the other rack first if it is currently in the way."
    )
    intention = (
        f"I therefore performed '{_stringify(actual_desc)}' (action {action_idx}), "
        f"an additional rack operation not present in the human plan."
    )
    return f"{belief} {desire} {intention}"


def _explain_load_missing_in_simple(target_label: str, actual_task) -> str:
    """A load task exists in the actual plan but has no counterpart in the simple plan."""
    belief = (
        f"I found '{target_label}' in my item list "
        f"but it has no corresponding task in the human plan."
    )
    desire = "My goal is to load every item I was given exactly once."
    intention = (
        f"I included a load task for '{target_label}' in my plan "
        f"because it was present in the items I received."
    )
    return f"{belief} {desire} {intention}"


def _explain_load_missing_in_actual(target_label: str) -> str:
    """A load task exists in the simple plan but is absent from the actual plan."""
    belief = (
        f"'{target_label}' appears in the human plan but not in my execution plan."
    )
    desire = "My goal is to load every item that was provided to me."
    intention = (
        f"'{target_label}' was not included in my plan. "
        f"This may indicate the item was omitted from my input list."
    )
    return f"{belief} {desire} {intention}"


def _explain_non_load_missing_in_simple(actual_desc: Optional[str]) -> str:
    belief = (
        f"The task '{_stringify(actual_desc)}' is present in my plan "
        f"but absent from the human plan."
    )
    desire = "My goal is to perform all required non-load operations (open, close dishwasher)."
    intention = (
        f"I included '{_stringify(actual_desc)}' in my plan. "
        f"This is likely a plan generation error."
    )
    return f"{belief} {desire} {intention}"


def _explain_non_load_missing_in_actual(simple_desc: Optional[str]) -> str:
    belief = (
        f"The task '{_stringify(simple_desc)}' is present in the human plan "
        f"but absent from my plan."
    )
    desire = "My goal is to perform all required non-load operations (open, close dishwasher)."
    intention = (
        f"I did not include '{_stringify(simple_desc)}' in my plan. "
        f"This is likely a plan generation error."
    )
    return f"{belief} {desire} {intention}"


def _explain_non_load_desc_mismatch(actual_desc: Optional[str],
                                    simple_desc: Optional[str]) -> str:
    belief = (
        "The description of this task differs between my plan and the human plan."
    )
    desire = "My goal is to perform all non-load operations correctly."
    intention = (
        f"I performed '{_stringify(actual_desc)}' where the human plan "
        f"expects '{_stringify(simple_desc)}'."
    )
    return f"{belief} {desire} {intention}"


def _compare_action_descriptions(
    actual_actions,
    simple_actions,
    actual_task,
    target_label: str,
    entries: list,
    actual_paths: set,
    simple_paths: set,
    actual_idx: Optional[int] = None,
    simple_idx: Optional[int] = None,
):
    max_actions = max(len(actual_actions), len(simple_actions))
    for action_idx in range(max_actions):

        if action_idx >= len(actual_actions):
            simple_desc = _get_attr(simple_actions[action_idx], "description")
            message = (
                f"Load task target '{target_label}', "
                f"Action {action_idx}: Missing in actual plan."
            )
            explanation = _explain_missing_action_in_actual(
                target_label, actual_task, action_idx, simple_desc
            )
            entries.append(MismatchEntry(message, explanation))
            _add_paths(actual_paths, simple_paths, None, simple_idx, f"actions.{action_idx}")
            continue

        if action_idx >= len(simple_actions):
            actual_desc = _get_attr(actual_actions[action_idx], "description")
            message = (
                f"Load task target '{target_label}', "
                f"Action {action_idx}: Missing in comparison plan."
            )
            explanation = _explain_missing_action_in_simple(
                target_label, actual_task, action_idx, actual_desc
            )
            entries.append(MismatchEntry(message, explanation))
            _add_paths(actual_paths, simple_paths, actual_idx, None, f"actions.{action_idx}")
            continue

        actual_desc = _get_attr(actual_actions[action_idx], "description")
        simple_desc = _get_attr(simple_actions[action_idx], "description")
        if actual_desc != simple_desc:
            message = (
                f"Load task target '{target_label}', "
                f"Action {action_idx}: description mismatch - "
                f"Actual: {_stringify(actual_desc)}, "
                f"Simple: {_stringify(simple_desc)}"
            )
            explanation = _explain_reorder_action(
                target_label, actual_task, action_idx, actual_desc, simple_desc
            )
            entries.append(MismatchEntry(message, explanation))
            _add_paths(
                actual_paths, simple_paths,
                actual_idx, simple_idx,
                f"actions.{action_idx}.description",
            )


# Public API


def findMismatch(actualPlan, simplePlan) -> list[str]:
    """Return human-readable mismatch messages only (no explanations)."""
    entries, _, _ = findMismatchDetailed(actualPlan, simplePlan)
    return [e.message for e in entries]


def findMismatchDetailed(actualPlan, simplePlan) -> tuple:
    """Compare two plans and return structured entries plus per-side highlight paths.

    Returns:
        (entries, actual_paths, simple_paths)
        - entries: list[MismatchEntry] - each has .message and .explanation
        - actual_paths: sorted list of dot-paths to highlight in the actual column
        - simple_paths: sorted list of dot-paths to highlight in the simple column
    """
    entries: list[MismatchEntry] = []
    actual_paths: set[str] = set()
    simple_paths: set[str] = set()

    actual_tasks = _get_tasks(actualPlan)
    simple_tasks = _get_tasks(simplePlan)

    actual_non_load, simple_non_load = [], []
    actual_load, simple_load = [], []

    for idx, task in enumerate(actual_tasks):
        (actual_load if _is_load_task(task) else actual_non_load).append(
            (idx, task, _task_target_key(task)) if _is_load_task(task) else (idx, task)
        )
    for idx, task in enumerate(simple_tasks):
        (simple_load if _is_load_task(task) else simple_non_load).append(
            (idx, task, _task_target_key(task)) if _is_load_task(task) else (idx, task)
        )

    # Non-load tasks
    max_non_load = max(len(actual_non_load), len(simple_non_load))
    for pos in range(max_non_load):

        if pos >= len(actual_non_load):
            simple_idx, simple_task = simple_non_load[pos]
            simple_desc = _get_attr(simple_task, "description")
            entries.append(MismatchEntry(
                f"Non-load task missing in actual plan: '{_stringify(simple_desc)}' (simple index {simple_idx}).",
                _explain_non_load_missing_in_actual(simple_desc),
            ))
            _add_paths(actual_paths, simple_paths, None, simple_idx, "description")
            continue

        if pos >= len(simple_non_load):
            actual_idx, actual_task = actual_non_load[pos]
            actual_desc = _get_attr(actual_task, "description")
            entries.append(MismatchEntry(
                f"Non-load task missing in comparison plan: '{_stringify(actual_desc)}' (actual index {actual_idx}).",
                _explain_non_load_missing_in_simple(actual_desc),
            ))
            _add_paths(actual_paths, simple_paths, actual_idx, None, "description")
            continue

        actual_idx, actual_task = actual_non_load[pos]
        simple_idx, simple_task = simple_non_load[pos]
        actual_desc = _get_attr(actual_task, "description")
        simple_desc = _get_attr(simple_task, "description")

        if actual_desc != simple_desc:
            entries.append(MismatchEntry(
                f"Non-load task description mismatch at position {pos} - "
                f"Actual: {_stringify(actual_desc)}, Simple: {_stringify(simple_desc)}",
                _explain_non_load_desc_mismatch(actual_desc, simple_desc),
            ))
            _add_paths(actual_paths, simple_paths, actual_idx, simple_idx, "description")

    # Load tasks (correlated by target name)
    simple_load_by_target: dict = {}
    for simple_idx, simple_task, target_key in simple_load:
        simple_load_by_target.setdefault(target_key, []).append((simple_idx, simple_task))

    for actual_idx, actual_task, target_key in actual_load:
        target_label = target_key if target_key is not None else "<unknown target>"
        candidates = simple_load_by_target.get(target_key, [])

        if not candidates:
            actual_desc = _get_attr(actual_task, "description")
            entries.append(MismatchEntry(
                f"Load task missing in comparison plan for target '{target_label}': {_stringify(actual_desc)}",
                _explain_load_missing_in_simple(target_label, actual_task),
            ))
            _add_paths(actual_paths, simple_paths, actual_idx, None, "description")
            continue

        simple_idx, simple_task = candidates.pop(0)
        actual_desc = _get_attr(actual_task, "description")
        simple_desc = _get_attr(simple_task, "description")

        if actual_idx != simple_idx:
            entries.append(MismatchEntry(
                f"Load task reordered for target '{target_label}' "
                f"(actual index {actual_idx}, simple index {simple_idx}).",
                _explain_sequential(target_label, actual_task, actual_idx, simple_idx),
            ))
            _add_paths(actual_paths, simple_paths, actual_idx, simple_idx, None)

        if actual_desc != simple_desc:
            entries.append(MismatchEntry(
                f"Load task description mismatch for target '{target_label}' - "
                f"Actual: {_stringify(actual_desc)}, Simple: {_stringify(simple_desc)}",
                _explain_sequential(target_label, actual_task, actual_idx, simple_idx),
            ))
            _add_paths(actual_paths, simple_paths, actual_idx, simple_idx, "description")

        _compare_action_descriptions(
            _get_actions(actual_task),
            _get_actions(simple_task),
            actual_task, target_label,
            entries, actual_paths, simple_paths,
            actual_idx, simple_idx,
        )

    # Tasks in simple plan with no match in actual plan
    for target_key, pending in simple_load_by_target.items():
        target_label = target_key if target_key is not None else "<unknown target>"
        for simple_idx, simple_task in pending:
            simple_desc = _get_attr(simple_task, "description")
            entries.append(MismatchEntry(
                f"Load task missing in actual plan for target '{target_label}': "
                f"{_stringify(simple_desc)} (simple index {simple_idx}).",
                _explain_load_missing_in_actual(target_label),
            ))
            _add_paths(actual_paths, simple_paths, None, simple_idx, "description")

    return entries, sorted(actual_paths), sorted(simple_paths)