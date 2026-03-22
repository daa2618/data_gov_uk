from __future__ import annotations

import pytest
from data_gov_uk.utils.strings_and_lists import (
    StringOperations,
    ListOperations,
    ConversionError,
    ClassIntiationError,
)


# ── StringOperations ────────────────────────────────────────────────


class TestStringOperationsConvertToInteger:
    def test_simple_integer(self):
        assert StringOperations("42").convert_to_integer() == 42

    def test_with_comma(self):
        assert StringOperations("1,000").convert_to_integer() == 1000

    def test_k_suffix(self):
        assert StringOperations("5K").convert_to_integer() == 5000

    def test_m_suffix(self):
        assert StringOperations("2M").convert_to_integer() == 2_000_000

    def test_float_with_m_suffix(self):
        assert StringOperations("2.5M").convert_to_integer() == 2_500_000

    def test_no_number_raises(self):
        with pytest.raises(ConversionError):
            StringOperations("abc").convert_to_integer()


class TestStringOperationsConvertToFloat:
    def test_simple_float(self):
        assert StringOperations("3.14").convert_to_float() == pytest.approx(3.14)

    def test_k_suffix(self):
        assert StringOperations("1.5K").convert_to_float() == pytest.approx(1500.0)

    def test_integer_string(self):
        assert StringOperations("7").convert_to_float() == pytest.approx(7.0)


# ── ListOperations ──────────────────────────────────────────────────


class TestListOperationsSearchString:
    def test_raises_when_none(self):
        lo = ListOperations(["a", "b"])
        with pytest.raises(ClassIntiationError):
            _ = lo.search_string

    def test_setter_works(self):
        lo = ListOperations(["a", "b"])
        lo.search_string = "test"
        assert lo.search_string == "test"


class TestGetMatchingScores:
    def test_returns_floats_between_0_and_1(self):
        lo = ListOperations(["apple", "banana"], search_string="apple")
        scores = lo._get_matching_scores_for_string()
        assert len(scores) == 2
        assert all(0 <= s <= 1 for s in scores)

    def test_empty_strings_skipped(self):
        lo = ListOperations(["apple", "", "banana"], search_string="apple")
        scores = lo._get_matching_scores_for_string()
        assert len(scores) == 2


class TestGetBestMatchingString:
    def test_exact_match(self):
        lo = ListOperations(["cat", "car", "bat"], search_string="cat")
        assert lo.get_best_matching_string() == "cat"

    def test_closest_match(self):
        lo = ListOperations(["running", "swimming", "cycling"], search_string="runner")
        result = lo.get_best_matching_string()
        assert result == "running"


class TestSearchListBySnowball:
    def test_finds_stemmed_match(self):
        lo = ListOperations(
            ["department-for-transport", "environment-agency"],
            search_string="transport",
        )
        result = lo.search_list_by_snowball()
        assert result is not None
        assert "department-for-transport" in result

    def test_returns_none_on_no_match(self):
        lo = ListOperations(["alpha", "beta"], search_string="zzzzz")
        assert lo.search_list_by_snowball() is None


class TestSearchListByStringForMetric:
    def test_float_threshold(self):
        lo = ListOperations(
            ["apple", "application", "banana"],
            search_string="apple",
        )
        result = lo.search_list_by_string_for_metric(0.5)
        assert result is not None
        assert "apple" in result

    def test_mean_metric(self):
        lo = ListOperations(
            ["apple", "application", "banana"],
            search_string="apple",
        )
        result = lo.search_list_by_string_for_metric("mean")
        assert result is not None

    def test_median_metric(self):
        lo = ListOperations(
            ["apple", "application", "banana"],
            search_string="apple",
        )
        result = lo.search_list_by_string_for_metric("median")
        assert result is not None

    def test_quantile_metric(self):
        lo = ListOperations(
            ["apple", "application", "banana"],
            search_string="apple",
        )
        result = lo.search_list_by_string_for_metric("0.75")
        assert result is not None

    def test_returns_none_for_impossible_threshold(self):
        lo = ListOperations(["aaa", "bbb"], search_string="zzz")
        result = lo.search_list_by_string_for_metric(0.99)
        assert result is None


class TestGetUniqueSortedElements:
    def test_basic(self):
        lo = ListOperations([3, 1, 2, 2])
        assert lo.get_unique_sorted_elements() == [1, 2, 3]

    def test_nested_lists(self):
        lo = ListOperations([[1, 2], [2, 3]])
        assert lo.get_unique_sorted_elements() == [1, 2, 3]

    def test_empty_raises(self):
        lo = ListOperations([])
        with pytest.raises(ValueError):
            lo.get_unique_sorted_elements()

    def test_filters_falsy(self):
        lo = ListOperations(["a", "", None, "b"])
        result = lo.get_unique_sorted_elements()
        assert "" not in result
        assert None not in result


class TestGetUniqueSortedElementsByKey:
    def test_deduplicates_by_key(self):
        data = [
            {"id": 1, "name": "apple"},
            {"id": 2, "name": "banana"},
            {"id": 1, "name": "apple"},
        ]
        lo = ListOperations(data)
        result = lo.get_unique_sorted_elements_by_key("id")
        assert len(result) == 2

    def test_sorts_by_sort_key(self):
        data = [
            {"id": 1, "name": "banana", "order": 2},
            {"id": 2, "name": "apple", "order": 1},
        ]
        lo = ListOperations(data)
        result = lo.get_unique_sorted_elements_by_key("id", "order")
        assert result[0]["order"] == 1

    def test_missing_key_raises(self):
        data = [{"id": 1}]
        lo = ListOperations(data)
        with pytest.raises(KeyError):
            lo.get_unique_sorted_elements_by_key("missing_key")

    def test_empty_raises(self):
        lo = ListOperations([])
        with pytest.raises(ClassIntiationError):
            lo.get_unique_sorted_elements_by_key("id")


class TestGetSingleResultDict:
    def test_one_item(self):
        lo = ListOperations([{"key": "value"}])
        assert lo.get_single_result_dict() == {"key": "value"}

    def test_multiple_raises(self):
        lo = ListOperations([{"a": 1}, {"b": 2}])
        with pytest.raises(ValueError, match="More than one"):
            lo.get_single_result_dict()

    def test_empty_raises(self):
        lo = ListOperations([])
        with pytest.raises(ValueError, match="No matching"):
            lo.get_single_result_dict()
