"""Formatting helpers."""
from __future__ import annotations

def rupiah(value: float | int) -> str:
    """Format a number as Indonesian Rupiah."""
    return f"Rp{value:,.0f}".replace(",", ".")
