import pandas as pd
import pytest

from scripts.build_tickets import deduplicate_tickets


def test_deduplicates_same_ticket_id_within_year():
    tickets = pd.DataFrame(
        {
            "year": ["2025", "2025", "2026"],
            "bi_id": ["123", "123", "123"],
            "street": ["MAIN ST", "MAIN ST", "OAK ST"],
        }
    )

    result, duplicates_removed = deduplicate_tickets(tickets)

    assert duplicates_removed == 1
    assert result[["year", "bi_id", "street"]].values.tolist() == [
        ["2025", "123", "MAIN ST"],
        ["2026", "123", "OAK ST"],
    ]


def test_reuses_ticket_id_across_years_without_dropping_rows():
    tickets = pd.DataFrame(
        {
            "year": ["2025", "2026"],
            "bi_id": ["4784906", "4784906"],
            "street": ["KINGSWAY", "WILLOW ST"],
        }
    )

    result, duplicates_removed = deduplicate_tickets(tickets)

    assert duplicates_removed == 0
    assert len(result) == 2


def test_rejects_missing_ticket_key():
    tickets = pd.DataFrame({"year": ["2025", "2026"], "bi_id": ["123", ""]})

    with pytest.raises(ValueError, match="year and bi_id must be present"):
        deduplicate_tickets(tickets)


def test_rejects_conflicting_rows_within_year():
    tickets = pd.DataFrame(
        {
            "year": ["2025", "2025"],
            "bi_id": ["123", "123"],
            "street": ["MAIN ST", "OAK ST"],
        }
    )

    with pytest.raises(ValueError, match="Conflicting ticket records"):
        deduplicate_tickets(tickets)
