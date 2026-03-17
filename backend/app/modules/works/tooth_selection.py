from __future__ import annotations

from typing import Any, Iterable


PERMANENT_TOOTH_ROWS = (
    ("18", "17", "16", "15", "14", "13", "12", "11"),
    ("21", "22", "23", "24", "25", "26", "27", "28"),
    ("48", "47", "46", "45", "44", "43", "42", "41"),
    ("31", "32", "33", "34", "35", "36", "37", "38"),
)

PRIMARY_TOOTH_ROWS = (
    ("55", "54", "53", "52", "51"),
    ("61", "62", "63", "64", "65"),
    ("85", "84", "83", "82", "81"),
    ("71", "72", "73", "74", "75"),
)

TOOTH_ORDER = {
    tooth_code: index
    for index, tooth_code in enumerate(
        [*PERMANENT_TOOTH_ROWS[0], *PERMANENT_TOOTH_ROWS[1], *PERMANENT_TOOTH_ROWS[2], *PERMANENT_TOOTH_ROWS[3], *PRIMARY_TOOTH_ROWS[0], *PRIMARY_TOOTH_ROWS[1], *PRIMARY_TOOTH_ROWS[2], *PRIMARY_TOOTH_ROWS[3]]
    )
}

SURFACE_LABELS = {
    "mesial": "M",
    "distal": "D",
    "vestibular": "V",
    "oral": "O",
    "occlusal": "Oc",
    "incisal": "I",
}

STATE_LABELS = {
    "target": "работа",
    "missing": "отсутствует",
}


def serialize_tooth_selection(items: Iterable[Any]) -> list[dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}

    for item in items:
        raw_item = item.model_dump(mode="json") if hasattr(item, "model_dump") else dict(item)
        tooth_code = str(raw_item.get("tooth_code", "")).strip()
        if not tooth_code:
            continue

        surfaces = [str(surface) for surface in raw_item.get("surfaces", []) if surface]
        unique_surfaces = list(dict.fromkeys(surfaces))
        normalized[tooth_code] = {
            "tooth_code": tooth_code,
            "state": str(raw_item.get("state", "target")),
            "surfaces": unique_surfaces,
        }

    return sorted(normalized.values(), key=lambda item: TOOTH_ORDER.get(item["tooth_code"], 10_000))


def build_tooth_formula_from_selection(items: Iterable[Any]) -> str | None:
    normalized = serialize_tooth_selection(items)
    if not normalized:
        return None

    selected: list[str] = []
    missing: list[str] = []

    for item in normalized:
        tooth_code = item["tooth_code"]
        surface_codes = [_surface_code(surface) for surface in item.get("surfaces", [])]
        suffix = f" ({', '.join(surface_codes)})" if surface_codes else ""
        rendered = f"{tooth_code}{suffix}"
        if item.get("state") == "missing":
            missing.append(rendered)
        else:
            selected.append(rendered)

    parts: list[str] = []
    if selected:
        parts.append(", ".join(selected))
    if missing:
        parts.append(f"отсутствуют: {', '.join(missing)}")

    return "; ".join(parts) or None


def build_tooth_selection_search_blob(items: Iterable[Any]) -> str | None:
    normalized = serialize_tooth_selection(items)
    if not normalized:
        return None

    tokens: list[str] = []
    for item in normalized:
        tooth_code = item["tooth_code"]
        tokens.append(tooth_code)
        tokens.append(STATE_LABELS.get(str(item.get("state")), str(item.get("state"))))
        for surface in item.get("surfaces", []):
            tokens.append(_surface_code(surface))

    return " ".join(dict.fromkeys(filter(None, tokens))) or None


def _surface_code(surface: str) -> str:
    return SURFACE_LABELS.get(surface, surface)
