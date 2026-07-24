"""
MuleTrace AI — Helper Utilities.

General purpose helper utilities for currency formatting, dictionary cleaning, and masking.
"""

from typing import Any


def format_currency_inr(amount: float) -> str:
    """Format numeric amount into Indian Rupee currency string.

    Args:
        amount: Numeric amount (e.g. 50000.0)

    Returns:
        Formatted string (e.g. '₹50,000.00').
    """
    return f"₹{amount:,.2f}"


def mask_account_number(account_number: str) -> str:
    """Mask account number for privacy compliance (shows last 4 digits).

    Args:
        account_number: Raw account string (e.g. '123456789012')

    Returns:
        Masked string (e.g. 'XXXX9012').
    """
    if len(account_number) <= 4:
        return account_number
    return f"XXXX{account_number[-4:]}"


def clean_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Remove None values from dictionary.

    Args:
        data: Input dictionary.

    Returns:
        Filtered dictionary without None fields.
    """
    return {k: v for k, v in data.items() if v is not None}
