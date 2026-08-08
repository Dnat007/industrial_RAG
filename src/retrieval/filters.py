from datetime import datetime
from typing import Iterable


def _escape_odata(value: str) -> str:
    """
    Escape a string for use inside an OData string literal.
    """
    return value.replace("'", "''")


def _search_in(field: str, values: Iterable[str]) -> str | None:
    """
    Build:

        search.in(field, 'value1,value2')

    Useful when a field can match one of many values.
    """

    values = [
        _escape_odata(str(value).strip())
        for value in values
        if str(value).strip()
    ]

    if not values:
        return None

    joined_values = ",".join(values)

    return f"search.in({field}, '{joined_values}', ',')"


def build_filter(
    allowed_access_levels: list[str] | None = None,
    departments: list[str] | None = None,
    versions: list[str] | None = None,
    document_ids: list[str] | None = None,
    effective_date_before: datetime | None = None,
) -> str | None:
    """
    Build an Azure AI Search OData filter.

    All different filter categories are combined with AND.

    Within the same category, multiple values are combined
    using search.in().

    Example:

        allowed_access_levels=["internal", "public"]
        departments=["HR"]

    becomes:

        search.in(access_level, 'internal,public', ',')
        and
        search.in(department, 'HR', ',')
    """

    filters: list[str] = []

    # ---------------------------------------------------------
    # 1. Security / access filtering
    # ---------------------------------------------------------

    if allowed_access_levels:
        expression = _search_in(
            "access_level",
            allowed_access_levels,
        )

        if expression:
            filters.append(expression)

    # ---------------------------------------------------------
    # 2. Department filtering
    # ---------------------------------------------------------

    if departments:
        expression = _search_in(
            "department",
            departments,
        )

        if expression:
            filters.append(expression)

    # ---------------------------------------------------------
    # 3. Version filtering
    # ---------------------------------------------------------

    if versions:
        expression = _search_in(
            "version",
            versions,
        )

        if expression:
            filters.append(expression)

    # ---------------------------------------------------------
    # 4. Specific document filtering
    # ---------------------------------------------------------

    if document_ids:
        expression = _search_in(
            "document_id",
            document_ids,
        )

        if expression:
            filters.append(expression)

    # ---------------------------------------------------------
    # 5. Effective date
    #
    # Only retrieve documents whose effective date is
    # less than or equal to the supplied date.
    # ---------------------------------------------------------

    if effective_date_before:

        effective_date = (
            effective_date_before
            .isoformat()
        )

        filters.append(
            f"effective_date le {effective_date}"
        )

    # ---------------------------------------------------------
    # No filters
    # ---------------------------------------------------------

    if not filters:
        return None

    # Different categories must ALL match.
    return " and ".join(
        f"({expression})"
        for expression in filters
    )