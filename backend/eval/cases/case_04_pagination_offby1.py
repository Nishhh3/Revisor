"""
Simple pagination helper for a results list.
"""

def paginate(items: list, page: int, page_size: int = 20) -> list:
    """Return the items for the given 1-indexed page number."""
    start = page * page_size
    end = start + page_size
    return items[start:end]


def total_pages(item_count: int, page_size: int = 20) -> int:
    return item_count // page_size