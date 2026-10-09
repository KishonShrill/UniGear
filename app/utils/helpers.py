"""General helper utilities for data formatting and conversion."""
from typing import Tuple


def convert_size(size_number: int) -> str:
    """Convert numeric size ID (1-6) to its corresponding label.

    Args:
        size_number: Numeric size from 1 to 6.

    Returns:
        String label ('XS', 'S', 'M', 'L', 'XL', '2XL').

    Raises:
        ValueError: If size_number is not between 1 and 6.
    """
    size_map = {
        1: "XS",
        2: "S",
        3: "M",
        4: "L",
        5: "XL",
        6: "2XL",
    }
    if size_number not in size_map:
        raise ValueError(f"Invalid size number. Must be between 1 and 6. Received: {size_number}")
    return size_map[size_number]


def split_address(address_str: str | None) -> Tuple[str, str, str]:
    """Split comma-separated address into (street, barangay, city).

    Args:
        address_str: Full address string formatted as "street, barangay, city".

    Returns:
        Tuple of (street, barangay, city).
    """
    if not address_str:
        return ("", "", "")
    parts = [p.strip() for p in address_str.split(",")]
    street = parts[0] if len(parts) > 0 else ""
    barangay = parts[1] if len(parts) > 1 else ""
    city = parts[2] if len(parts) > 2 else ""
    return (street, barangay, city)


def format_address(street: str | None, barangay: str | None, city: str | None) -> str:
    """Format address parts into a single comma-separated address string.

    Args:
        street: Street address or house number.
        barangay: Barangay or district.
        city: City or municipality.

    Returns:
        Comma-separated address string.
    """
    parts = [p.strip() for p in (street, barangay, city) if p and p.strip()]
    return ", ".join(parts)
