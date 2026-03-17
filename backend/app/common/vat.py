from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Literal


VatMode = Literal["without_vat", "vat_0", "vat_5", "vat_7", "vat_10", "vat_20"]

VAT_OPTIONS: dict[VatMode, dict[str, Decimal | str]] = {
    "without_vat": {"label": "Без налога (НДС)", "rate": Decimal("0.00")},
    "vat_0": {"label": "НДС 0%", "rate": Decimal("0.00")},
    "vat_5": {"label": "НДС 5%", "rate": Decimal("0.05")},
    "vat_7": {"label": "НДС 7%", "rate": Decimal("0.07")},
    "vat_10": {"label": "НДС 10%", "rate": Decimal("0.10")},
    "vat_20": {"label": "НДС 20%", "rate": Decimal("0.20")},
}

DEFAULT_VAT_MODE: VatMode = "without_vat"
MONEY_QUANT = Decimal("0.01")


def resolve_vat_mode(vat_mode: str | None, vat_label: str | None = None) -> VatMode:
    if vat_mode in VAT_OPTIONS:
        return vat_mode

    normalized = (vat_label or "").lower()
    if "20" in normalized:
        return "vat_20"
    if "10" in normalized:
        return "vat_10"
    if "7" in normalized:
        return "vat_7"
    if "5" in normalized:
        return "vat_5"
    if "0" in normalized:
        return "vat_0"
    return DEFAULT_VAT_MODE


def get_vat_label(vat_mode: str | None, vat_label: str | None = None) -> str:
    resolved_mode = resolve_vat_mode(vat_mode, vat_label)
    return str(VAT_OPTIONS[resolved_mode]["label"])


def get_vat_rate(vat_mode: str | None, vat_label: str | None = None) -> Decimal:
    resolved_mode = resolve_vat_mode(vat_mode, vat_label)
    return Decimal(str(VAT_OPTIONS[resolved_mode]["rate"]))


def build_vat_snapshot(vat_mode: str | None, vat_label: str | None = None) -> dict[str, Decimal | str]:
    resolved_mode = resolve_vat_mode(vat_mode, vat_label)
    rate = get_vat_rate(resolved_mode)
    return {
        "vat_mode": resolved_mode,
        "vat_label": get_vat_label(resolved_mode),
        "vat_rate_percent": (rate * Decimal("100")).quantize(MONEY_QUANT),
    }


def calculate_vat_breakdown(amount_without_vat: Decimal, vat_mode: str | None, vat_label: str | None = None) -> dict[str, Decimal | str]:
    subtotal = amount_without_vat.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    snapshot = build_vat_snapshot(vat_mode, vat_label)
    rate = get_vat_rate(str(snapshot["vat_mode"]))
    vat_amount = (subtotal * rate).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    total_with_vat = (subtotal + vat_amount).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    return {
        **snapshot,
        "subtotal_without_vat": subtotal,
        "vat_amount": vat_amount,
        "total_with_vat": total_with_vat,
    }
