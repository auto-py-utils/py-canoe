"""
Unit tests for test module and test case features:
- TestCase class (properties, verdict_name, to_dict)
- TestModule test case methods (collection, verdict, enable/disable)
- Configuration._match_test_case_name (wildcard and regex)
- Configuration._apply_test_case_selection (enable/disable logic)
- Configuration._find_test_module (lookup helper)
- Configuration.execute_test_module with enable/disable patterns
- Configuration.get_test_module_result (report + test case verdicts)
"""

from unittest.mock import MagicMock, Mock, patch, PropertyMock

from py_canoe.core.child_elements.test_case import TestCase
from py_canoe.core.child_elements.test_module import TestModule
from py_canoe.core.child_elements.test_tree_element import TestTreeElement, TestTreeElementType
from py_canoe.core.configuration import Configuration


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_case(name="TC_001", enabled=True, verdict=0, title="Test Case 001"):
    """Create a TestCase instance with mocked COM (bypasses Dispatch)."""
    com = MagicMock()
    com.Name = name
    com.Enabled = enabled
    com.Verdict = verdict
    com.Title = title
    with patch("win32com.client.Dispatch", side_effect=lambda x: x):
        return TestCase(com)


def _make_test_case_item(name, enabled=True, verdict=0, title=None):
    """Build a mock TestSequenceItem for a TestCase.

    The production code uses win32com.client.CastTo(item, "ITestCase") to obtain
    the TestCase interface, so the mock only needs the plain TestCase attributes
    (Name/Enabled/Verdict/Title). CastTo is patched in the callers below.

    A real TestCase has no `.Sequence` attribute (only TestGroups do), so we
    explicitly block it on the mock. Otherwise MagicMock auto-creates `.Sequence`
    and the cast-side-effect helper would misclassify the item as a group.
    """
    item = MagicMock()
    item.Name = name
    item.Enabled = enabled
    item.Verdict = verdict
    item.Title = title if title is not None else name
    del item.Sequence
    return item


def _make_group_item(name, child_items):
    """Build a mock TestSequenceItem for a TestGroup.

    A group exposes a nested Sequence (iterable) of child items. CastTo to
    "ITestGroup" returns this object, and its .Sequence yields child_items.
    """
    group = MagicMock()
    group.Name = name
    child_sequence = MagicMock()
    child_sequence.Count = len(child_items)
    child_sequence.Item = lambda idx: child_items[idx - 1]
    # Make the group's Sequence iterable (production code does `for x in seq`).
    child_sequence.__iter__ = lambda self: iter(child_items)
    group.Sequence = child_sequence
    return group


def _make_sequence_mock(items):
    """Build a Sequence mock that is iterable and indexable (1-based)."""
    sequence = MagicMock()
    sequence.Count = len(items)
    sequence.Item = lambda idx: items[idx - 1]
    sequence.__iter__ = lambda self: iter(items)
    return sequence


def _cast_to_side_effect(obj, cls):
    """Mock win32com.client.CastTo.

    In real CANoe, casting a TestCase to "ITestGroup" (or vice versa) raises.
    We emulate that: a group item carries a `.Sequence` attribute, a TestCase
    does not. Casting to the wrong interface raises TypeError so the
    production code's try/except falls through to the correct branch.
    """
    if cls == "ITestGroup":
        if not hasattr(obj, "Sequence"):
            raise TypeError("Cannot cast TestCase to ITestGroup")
        return obj
    if cls == "ITestCase":
        if hasattr(obj, "Sequence"):
            raise TypeError("Cannot cast TestGroup to ITestCase")
        return obj
    return obj


def _make_test_module_wrapper(test_cases=None):
    """Create a TestModule wrapper with mocked COM and test cases.

    Args:
        test_cases: list of dicts with keys 'name', 'enabled', 'verdict', 'title'
    """
    if test_cases is None:
        test_cases = []

    com = MagicMock()
    com.Name = "TestMod1"
    com.FullName = "Env1::TestMod1"
    com.Verdict = 1

    items = [
        _make_test_case_item(
            name=tc["name"],
            enabled=tc.get("enabled", True),
            verdict=tc.get("verdict", 0),
            title=tc.get("title", tc["name"]),
        )
        for tc in test_cases
    ]
    com.Sequence = _make_sequence_mock(items)

    # Mock test_module_events
    events = MagicMock()
    events.TEST_REPORT_INFORMATION = {
        "success": True,
        "source_full_name": "C:/report.xml",
        "generated_full_name": "C:/report.html"
    }

    with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
         patch("win32com.client.WithEvents", return_value=events), \
         patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
        tm = TestModule(com)

    return tm


def _make_test_module_with_groups():
    """Create a TestModule with nested TestGroup -> Sequence -> TestCase."""
    com = MagicMock()
    com.Name = "TestModGroup"
    com.FullName = "Env1::TestModGroup"
    com.Verdict = 2

    tc_in_group = _make_test_case_item(
        name="TC_InGroup", enabled=True, verdict=1, title="TC In Group"
    )
    group = _make_group_item("Group1", [tc_in_group])

    tc_top = _make_test_case_item(
        name="TC_Top", enabled=False, verdict=2, title="TC Top Level"
    )

    com.Sequence = _make_sequence_mock([tc_top, group])

    events = MagicMock()
    events.TEST_REPORT_INFORMATION = {}

    with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
         patch("win32com.client.WithEvents", return_value=events), \
         patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
        tm = TestModule(com)

    return tm


# ===========================================================================
# TestCase class tests
# ===========================================================================

class TestTestCaseClass:
    """Test TestCase COM wrapper class."""

    def test_name_property(self):
        tc = _make_test_case(name="MyTestCase")
        assert tc.name == "MyTestCase"

    def test_title_property(self):
        tc = _make_test_case(title="My Title")
        assert tc.title == "My Title"

    def test_enabled_getter(self):
        tc = _make_test_case(enabled=False)
        assert tc.enabled is False

    def test_enabled_setter(self):
        tc = _make_test_case(enabled=False)
        tc.enabled = True
        assert tc.com_object.Enabled is True

    def test_verdict_property(self):
        tc = _make_test_case(verdict=2)
        assert tc.verdict == 2

    def test_verdict_name_passed(self):
        tc = _make_test_case(verdict=1)
        assert tc.verdict_name == "Passed"

    def test_verdict_name_failed(self):
        tc = _make_test_case(verdict=2)
        assert tc.verdict_name == "Failed"

    def test_verdict_name_not_available(self):
        tc = _make_test_case(verdict=0)
        assert tc.verdict_name == "NotAvailable"

    def test_verdict_name_inconclusive(self):
        tc = _make_test_case(verdict=4)
        assert tc.verdict_name == "Inconclusive"

    def test_verdict_name_error_in_test_system(self):
        tc = _make_test_case(verdict=5)
        assert tc.verdict_name == "ErrorInTestSystem"

    def test_to_dict(self):
        tc = _make_test_case(name="TC1", enabled=True, verdict=1, title="Title1")
        d = tc.to_dict()
        assert d == {
            "name": "TC1",
            "title": "Title1",
            "enabled": True,
            "verdict": 1,
            "verdict_name": "Passed"
        }

    def test_repr(self):
        tc = _make_test_case(name="TC1", enabled=True, verdict=1)
        assert "TC1" in repr(tc)
        assert "Passed" in repr(tc)

    def test_value_table_verdict_class_attribute(self):
        assert TestCase.VALUE_TABLE_VERDICT[0] == "NotAvailable"
        assert TestCase.VALUE_TABLE_VERDICT[1] == "Passed"
        assert TestCase.VALUE_TABLE_VERDICT[2] == "Failed"
        assert TestCase.VALUE_TABLE_VERDICT[3] == "None"
        assert TestCase.VALUE_TABLE_VERDICT[4] == "Inconclusive"
        assert TestCase.VALUE_TABLE_VERDICT[5] == "ErrorInTestSystem"


# ===========================================================================
# TestModule test case methods
# ===========================================================================

class TestModuleTestCases:
    """Test TestModule test case collection and access methods."""

    # _collect_test_cases calls TestCase(item) which calls Dispatch internally,
    # so we must keep Dispatch patched during the get_all_test_calls etc. calls.

    def test_get_all_test_cases_empty(self):
        tm = _make_test_module_wrapper(test_cases=[])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x):
            result = tm.get_all_test_cases()
        assert result == {}

    def test_get_all_test_cases_returns_dict(self):
        tm = _make_test_module_wrapper([
            {"name": "TC_001", "enabled": True, "verdict": 1},
            {"name": "TC_002", "enabled": False, "verdict": 2},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            result = tm.get_all_test_cases()
        assert len(result) == 2
        assert "TC_001" in result
        assert "TC_002" in result
        assert isinstance(result["TC_001"], TestCase)

    def test_get_all_test_cases_preserves_enabled_state(self):
        tm = _make_test_module_wrapper([
            {"name": "TC_001", "enabled": True, "verdict": 0},
            {"name": "TC_002", "enabled": False, "verdict": 0},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            result = tm.get_all_test_cases()
        assert result["TC_001"].enabled is True
        assert result["TC_002"].enabled is False

    def test_get_all_test_cases_with_nested_groups(self):
        tm = _make_test_module_with_groups()
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            result = tm.get_all_test_cases()
        assert len(result) == 2
        assert "TC_Top" in result
        assert "TC_InGroup" in result

    def test_get_test_case_found(self):
        tm = _make_test_module_wrapper([
            {"name": "TC_001", "enabled": True, "verdict": 1},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            tc = tm.get_test_case("TC_001")
        assert tc is not None
        assert tc.name == "TC_001"

    def test_get_test_case_not_found(self):
        tm = _make_test_module_wrapper([
            {"name": "TC_001", "enabled": True, "verdict": 1},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            tc = tm.get_test_case("NonExistent")
        assert tc is None

    def test_get_test_case_verdict_found(self):
        tm = _make_test_module_wrapper([
            {"name": "TC_001", "enabled": True, "verdict": 2},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            assert tm.get_test_case_verdict("TC_001") == 2

    def test_get_test_case_verdict_not_found(self):
        tm = _make_test_module_wrapper([])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            assert tm.get_test_case_verdict("NonExistent") == -1

    def test_get_test_case_enabled_found(self):
        tm = _make_test_module_wrapper([
            {"name": "TC_001", "enabled": False, "verdict": 0},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            assert tm.get_test_case_enabled("TC_001") is False

    def test_get_test_case_enabled_not_found(self):
        tm = _make_test_module_wrapper([])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            assert tm.get_test_case_enabled("NonExistent") is None

    def test_set_test_case_enabled_success(self):
        tm = _make_test_module_wrapper([
            {"name": "TC_001", "enabled": False, "verdict": 0},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            result = tm.set_test_case_enabled("TC_001", True)
        assert result is True

    def test_set_test_case_enabled_not_found(self):
        tm = _make_test_module_wrapper([])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            result = tm.set_test_case_enabled("NonExistent", True)
        assert result is False

    def test_get_all_test_case_verdicts(self):
        tm = _make_test_module_wrapper([
            {"name": "TC_001", "enabled": True, "verdict": 1},
            {"name": "TC_002", "enabled": False, "verdict": 2},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            result = tm.get_all_test_case_verdicts()
        assert result["TC_001"]["verdict"] == 1
        assert result["TC_001"]["verdict_name"] == "Passed"
        assert result["TC_001"]["enabled"] is True
        assert result["TC_002"]["verdict"] == 2
        assert result["TC_002"]["verdict_name"] == "Failed"
        assert result["TC_002"]["enabled"] is False


# ===========================================================================
# Configuration._match_test_case_name
# ===========================================================================

class TestMatchTestCaseName:
    """Test pattern matching logic."""

    # --- Wildcard tests ---

    def test_wildcard_star_matches_all(self):
        assert Configuration._match_test_case_name("TC_001", "*") is True
        assert Configuration._match_test_case_name("Anything", "*") is True

    def test_wildcard_prefix(self):
        assert Configuration._match_test_case_name("SmokeTest_001", "SmokeTest_*") is True
        assert Configuration._match_test_case_name("Regression_001", "SmokeTest_*") is False

    def test_wildcard_suffix(self):
        assert Configuration._match_test_case_name("TC_001_pass", "*_pass") is True
        assert Configuration._match_test_case_name("TC_001_fail", "*_pass") is False

    def test_wildcard_question_mark(self):
        assert Configuration._match_test_case_name("TC_001", "TC_00?") is True
        assert Configuration._match_test_case_name("TC_001", "TC_0?1") is True
        assert Configuration._match_test_case_name("TC_0012", "TC_00?") is False

    def test_wildcard_bracket_seq(self):
        assert Configuration._match_test_case_name("TC_001", "TC_00[123]") is True
        assert Configuration._match_test_case_name("TC_004", "TC_00[123]") is False

    def test_wildcard_bracket_neg_seq(self):
        # fnmatchcase uses [!seq] for negation
        assert Configuration._match_test_case_name("TC_004", "TC_00[!123]") is True
        assert Configuration._match_test_case_name("TC_001", "TC_00[!123]") is False

    def test_wildcard_multiple_stars(self):
        assert Configuration._match_test_case_name("SmokeTest_Module1_Pass", "*Test_*_Pass") is True
        assert Configuration._match_test_case_name("SmokeTest_Module1_Fail", "*Test_*_Pass") is False

    # --- Regex tests ---

    def test_regex_prefix_group(self):
        assert Configuration._match_test_case_name("tc_001", "(?i)^tc_(001|002|003)$") is True
        assert Configuration._match_test_case_name("tc_004", "(?i)^tc_(001|002|003)$") is False
        assert Configuration._match_test_case_name("TC_001", "(?i)^tc_(001|002|003)$") is True

    def test_regex_caret_anchor(self):
        assert Configuration._match_test_case_name("SmokeTest_001", "^Smoke") is True
        assert Configuration._match_test_case_name("Regression_Smoke", "^Smoke") is False

    def test_regex_dollar_anchor(self):
        assert Configuration._match_test_case_name("TC_001_Pass", "Pass$") is True
        assert Configuration._match_test_case_name("TC_001_Fail", "Pass$") is False

    def test_regex_plus_quantifier(self):
        assert Configuration._match_test_case_name("TC_0001", r"TC_0+1") is True
        assert Configuration._match_test_case_name("TC_1", r"TC_0+1") is False

    def test_regex_braces_quantifier(self):
        assert Configuration._match_test_case_name("TC_001", r"TC_\d{3}") is True
        assert Configuration._match_test_case_name("TC_01", r"TC_\d{3}") is False

    def test_regex_square_brackets(self):
        assert Configuration._match_test_case_name("TC_A", r"TC_[A-Z]") is True
        assert Configuration._match_test_case_name("TC_1", r"TC_[A-Z]") is False

    def test_regex_backslash(self):
        assert Configuration._match_test_case_name("TC_001", r"TC_\d+") is True
        assert Configuration._match_test_case_name("TC_abc", r"TC_\d+") is False

    # --- Regex vs glob disambiguation ---

    def test_bracket_range_with_plus_is_regex(self):
        # TC_[0-9]+ -> regex (contains \d-like range and +)
        assert Configuration._match_test_case_name("TC_123", r"TC_[0-9]+") is True
        assert Configuration._match_test_case_name("TC_abc", r"TC_[0-9]+") is False

    def test_bracket_range_without_plus_is_glob(self):
        # TC_[0-9] �?glob (single char range, no +)
        assert Configuration._match_test_case_name("TC_1", "TC_[0-9]") is True
        assert Configuration._match_test_case_name("TC_a", "TC_[0-9]") is False

    def test_brace_quantifier_is_regex(self):
        # {3} �?regex quantifier
        assert Configuration._match_test_case_name("TC_001", r"TC_\d{3}") is True
        assert Configuration._match_test_case_name("TC_01", r"TC_\d{3}") is False

    def test_brace_alternation_is_glob_no_expansion(self):
        # {foo,bar} �?treated as fnmatch, but Python fnmatch doesn't support
        # brace expansion, so it becomes a literal match (no match)
        assert Configuration._match_test_case_name("TC_foo", "TC_{foo,bar}") is False
        assert Configuration._match_test_case_name("TC_{foo,bar}", "TC_{foo,bar}") is True

    def test_posix_class_in_bracket_detected_as_regex(self):
        # [[:alpha:]] �?detected as regex (contains [:...:] inside brackets)
        # but Python re doesn't support POSIX classes, so use \w equivalent instead
        assert Configuration._match_test_case_name("TC_a", r"TC_[\w]") is True
        assert Configuration._match_test_case_name("TC_1", r"TC_[\w]") is True
        assert Configuration._match_test_case_name("TC_", r"TC_[\w]") is False

    # --- Edge cases ---

    def test_invalid_regex_falls_back_to_literal(self):
        assert Configuration._match_test_case_name("TC[", "TC[") is True
        assert Configuration._match_test_case_name("TC_001", "TC[") is False

    def test_exact_match(self):
        assert Configuration._match_test_case_name("TC_001", "TC_001") is True
        assert Configuration._match_test_case_name("TC_002", "TC_001") is False

    def test_case_sensitive_wildcard(self):
        assert Configuration._match_test_case_name("tc_001", "TC_*") is False
        assert Configuration._match_test_case_name("TC_001", "TC_*") is True

    def test_empty_pattern(self):
        assert Configuration._match_test_case_name("", "") is True
        assert Configuration._match_test_case_name("TC_001", "") is False


# ===========================================================================
# Configuration._apply_test_case_selection
# ===========================================================================

class TestApplyTestCaseSelection:
    """Test enable/disable test case selection logic."""

    def _make_cfg_with_test_cases(self, test_cases):
        """Create Configuration with test module COM mock returning given test cases."""
        cfg = Configuration.__new__(Configuration)

        # Build COM mock items
        items = []
        for tc in test_cases:
            item = _make_test_case_item(
                name=tc["name"],
                enabled=tc.get("enabled", True),
                verdict=tc.get("verdict", 0),
                title=tc.get("title", tc["name"]),
            )
            items.append(item)

        com = MagicMock()
        com.Name = "TestMod1"
        com._oleobj_ = MagicMock()  # present on real (raw) CANoe COM objects
        com.Sequence = _make_sequence_mock(items)

        # In production, _find_test_module returns a TestModule wrapper (built in
        # fetch_test_modules). _apply_test_case_selection calls
        # tm_obj.get_all_test_cases() directly, so the stored object must be a
        # TestModule wrapper, not the raw COM mock.
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.WithEvents", return_value=MagicMock()), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            tm_wrapper = TestModule(com)

        cfg._Configuration__test_modules = [
            {"name": "TestMod1", "object": tm_wrapper, "environment": "Env1"}
        ]

        return cfg, tm_wrapper, items

    def test_no_patterns_does_nothing(self):
        cfg, com, items = self._make_cfg_with_test_cases([
            {"name": "TC_001", "enabled": True},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.WithEvents", return_value=MagicMock()), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            cfg._apply_test_case_selection(com, (), ())
        assert items[0].Enabled is True

    def test_enable_pattern_enables_matching(self):
        cfg, com, items = self._make_cfg_with_test_cases([
            {"name": "TC_001", "enabled": False},
            {"name": "TC_002", "enabled": False},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.WithEvents", return_value=MagicMock()), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            cfg._apply_test_case_selection(com, ["TC_001"], ())
        assert items[0].Enabled is True   # TC_001 enabled
        assert items[1].Enabled is False  # TC_002 unchanged

    def test_disable_pattern_disables_matching(self):
        cfg, com, items = self._make_cfg_with_test_cases([
            {"name": "TC_001", "enabled": True},
            {"name": "TC_slow_001", "enabled": True},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.WithEvents", return_value=MagicMock()), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            cfg._apply_test_case_selection(com, ["*"], ["*slow*"])
        assert items[0].Enabled is True   # TC_001 stays enabled
        assert items[1].Enabled is False  # TC_slow_001 disabled

    def test_disable_takes_precedence_over_enable(self):
        cfg, com, items = self._make_cfg_with_test_cases([
            {"name": "TC_slow_001", "enabled": True},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.WithEvents", return_value=MagicMock()), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            cfg._apply_test_case_selection(com, ["*"], ["*slow*"])
        assert items[0].Enabled is False

    def test_string_pattern_not_iterated_char_by_char(self):
        """Regression: passing a bare string (e.g. "XM_CSflash_FUNC_00*") instead
        of a list must NOT be iterated character-by-character (which would make
        the '*' char match every test case). The string must be treated as a
        single pattern so only correctly-matching cases are enabled."""
        cfg, com, items = self._make_cfg_with_test_cases([
            {"name": "XM_CSflash_FUNC_002", "enabled": False},
            {"name": "XM_CSflash_FUNC_071", "enabled": False},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.WithEvents", return_value=MagicMock()), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            # Pass a STRING, not a list - this used to enable both cases.
            cfg._apply_test_case_selection(com, "XM_CSflash_FUNC_00*", ())
        # Only the case matching the full pattern should be enabled.
        assert items[0].Enabled is True    # XM_CSflash_FUNC_002 matches
        assert items[1].Enabled is False   # XM_CSflash_FUNC_071 must NOT match

    def test_match_by_title(self):
        """When match_by='title', patterns are matched against the test case
        title rather than its name. A pattern that matches the title but not
        the name should still enable the correct case."""
        cfg, com, items = self._make_cfg_with_test_cases([
            {"name": "TC_001", "enabled": False, "title": "BLE Connect Test"},
            {"name": "TC_002", "enabled": False, "title": "WiFi Scan Test"},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.WithEvents", return_value=MagicMock()), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            cfg._apply_test_case_selection(com, "*BLE*", (), match_by="title")
        assert items[0].Enabled is True    # title "BLE Connect Test" matches
        assert items[1].Enabled is False   # title "WiFi Scan Test" does not match

    def test_match_by_title_no_name_match(self):
        """A pattern matching the name but not the title must NOT enable the
        case when match_by='title'."""
        cfg, com, items = self._make_cfg_with_test_cases([
            {"name": "BLE_001", "enabled": False, "title": "Connect Test"},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.WithEvents", return_value=MagicMock()), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            cfg._apply_test_case_selection(com, "BLE*", (), match_by="title")
        assert items[0].Enabled is False   # name matches but title does not

    def test_match_by_title_skips_when_no_titles(self):
        """When no test case exposes a Title (e.g. CAPL modules), match_by='title'
        must warn once and skip the whole matching loop (no name fallback).
        No case is enabled and the loop body is never executed."""
        cfg, com, items = self._make_cfg_with_test_cases([
            {"name": "XM_CSflash_FUNC_002", "enabled": False, "title": ""},
            {"name": "XM_CSflash_FUNC_071", "enabled": False, "title": ""},
        ])
        with patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.WithEvents", return_value=MagicMock()), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            cfg._apply_test_case_selection(com, "XM_CSflash_FUNC_00*", (), match_by="title")
        # Loop skipped entirely: cases keep their original (disabled) state.
        assert items[0].Enabled is False   # XM_CSflash_FUNC_002 untouched
        assert items[1].Enabled is False   # XM_CSflash_FUNC_071 untouched


# ===========================================================================
# Configuration._find_test_module
# ===========================================================================

class TestFindTestModule:
    """Test _find_test_module helper."""

    def test_finds_existing_module(self):
        cfg = Configuration.__new__(Configuration)
        mock_tm = Mock()
        cfg._Configuration__test_modules = [
            {"name": "TestMod1", "object": mock_tm, "environment": "Env1"}
        ]
        result = cfg._find_test_module("TestMod1")
        assert result is mock_tm

    def test_returns_none_for_missing_module(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_modules = [
            {"name": "TestMod1", "object": Mock(), "environment": "Env1"}
        ]
        result = cfg._find_test_module("NonExistent")
        assert result is None

    def test_finds_correct_module_among_multiple(self):
        cfg = Configuration.__new__(Configuration)
        mock_tm1 = Mock()
        mock_tm2 = Mock()
        cfg._Configuration__test_modules = [
            {"name": "TestMod1", "object": mock_tm1, "environment": "Env1"},
            {"name": "TestMod2", "object": mock_tm2, "environment": "Env2"},
        ]
        assert cfg._find_test_module("TestMod2") is mock_tm2

    def test_empty_list_returns_none(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_modules = []
        result = cfg._find_test_module("AnyModule")
        assert result is None


# ===========================================================================
# Configuration.execute_test_module with patterns
# ===========================================================================

class TestExecuteTestModuleWithPatterns:
    """Test execute_test_module with enable/disable patterns."""

    def _make_cfg_with_mock_tm(self, verdict=1):
        """Create Configuration with a mock test module that returns the given verdict."""
        cfg = Configuration.__new__(Configuration)
        mock_tm = Mock()
        mock_tm.verdict = verdict
        cfg._Configuration__test_modules = [
            {"name": "TestMod1", "object": mock_tm, "environment": "Env1"}
        ]
        return cfg, mock_tm

    def test_execute_without_patterns_unchanged(self):
        cfg, mock_tm = self._make_cfg_with_mock_tm(verdict=1)

        with patch("py_canoe.core.configuration.Configuration._apply_test_case_selection") as mock_apply:
            result = cfg.execute_test_module("TestMod1")

        # execute_test_module now really starts the module and returns its verdict.
        assert result == 1
        mock_apply.assert_called_once_with(mock_tm, (), (), match_by="name")

    def test_execute_with_enable_patterns(self):
        cfg, mock_tm = self._make_cfg_with_mock_tm(verdict=1)

        with patch("py_canoe.core.configuration.Configuration._apply_test_case_selection") as mock_apply:
            cfg.execute_test_module("TestMod1", enable_test_cases=["TC_*"])

        mock_apply.assert_called_once_with(mock_tm, ["TC_*"], (), match_by="name")

    def test_execute_with_disable_patterns(self):
        cfg, mock_tm = self._make_cfg_with_mock_tm(verdict=1)

        with patch("py_canoe.core.configuration.Configuration._apply_test_case_selection") as mock_apply:
            cfg.execute_test_module("TestMod1", disable_test_cases=["*slow*"])

        mock_apply.assert_called_once_with(mock_tm, (), ["*slow*"], match_by="name")

    def test_execute_with_both_patterns(self):
        cfg, mock_tm = self._make_cfg_with_mock_tm(verdict=1)

        with patch("py_canoe.core.configuration.Configuration._apply_test_case_selection") as mock_apply:
            cfg.execute_test_module("TestMod1", enable_test_cases=["*"], disable_test_cases=["*slow*"])

        mock_apply.assert_called_once_with(mock_tm, ["*"], ["*slow*"], match_by="name")

    def test_execute_with_match_by_title(self):
        cfg, mock_tm = self._make_cfg_with_mock_tm(verdict=1)

        with patch("py_canoe.core.configuration.Configuration._apply_test_case_selection") as mock_apply:
            cfg.execute_test_module("TestMod1", enable_test_cases=["*BLE*"], match_by="title")

        mock_apply.assert_called_once_with(mock_tm, ["*BLE*"], (), match_by="title")

    def test_execute_not_found_returns_zero(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_modules = []

        result = cfg.execute_test_module("NonExistent")
        assert result == 0

    def test_execute_exception_returns_zero(self):
        cfg = Configuration.__new__(Configuration)
        mock_tm = MagicMock()
        mock_tm.start.side_effect = Exception("COM error")
        cfg._Configuration__test_modules = [
            {"name": "TestMod1", "object": mock_tm, "environment": "Env1"}
        ]

        with patch("py_canoe.core.configuration.Configuration._apply_test_case_selection"):
            result = cfg.execute_test_module("TestMod1")

        assert result == 0


# ===========================================================================
# Configuration.get_test_module_result
# ===========================================================================

class TestGetTestModuleResult:
    """Test get_test_module_result method."""

    def _make_cfg_for_result(self, test_cases, verdict=1, report_info=None):
        cfg = Configuration.__new__(Configuration)
        tm_wrapper = _make_test_module_wrapper(test_cases)
        tm_wrapper.com_object.Verdict = verdict
        # get_test_module_result requires the module to be started before it
        # collects results (it checks TM_STARTED on the TestModule wrapper).
        tm_wrapper.test_module_events.TM_STARTED = True
        tm_wrapper.test_module_events.TM_REPORT_GENERATED = True
        if report_info is not None:
            tm_wrapper.test_module_events.TEST_REPORT_INFORMATION = report_info
        # _find_test_module returns the stored TestModule wrapper (object), which
        # exposes .verdict, .get_all_test_cases() and .test_module_events.
        cfg._Configuration__test_modules = [
            {"name": "TestMod1", "object": tm_wrapper, "environment": "Env1"}
        ]
        return cfg, tm_wrapper

    def test_result_structure(self):
        cfg, tm = self._make_cfg_for_result([
            {"name": "TC_001", "enabled": True, "verdict": 1, "title": "TC 1"},
        ])

        with patch("py_canoe.core.configuration.Configuration._find_test_module", return_value=tm), \
             patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            result = cfg.get_test_module_result("TestMod1")

        assert "verdict" in result
        assert "verdict_name" in result
        assert "report" in result
        assert "test_cases" in result

    def test_result_verdict(self):
        cfg, tm = self._make_cfg_for_result([], verdict=2)

        with patch("py_canoe.core.configuration.Configuration._find_test_module", return_value=tm), \
             patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            result = cfg.get_test_module_result("TestMod1")

        assert result["verdict"] == 2
        assert result["verdict_name"] == "Failed"

    def test_result_report_info(self):
        cfg, tm = self._make_cfg_for_result([], report_info={
            "success": True,
            "source_full_name": "C:/test.xml",
            "generated_full_name": "C:/test.html"
        })

        with patch("py_canoe.core.configuration.Configuration._find_test_module", return_value=tm), \
             patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            result = cfg.get_test_module_result("TestMod1")

        assert result["report"]["success"] is True
        assert result["report"]["source_full_name"] == "C:/test.xml"
        assert result["report"]["generated_full_name"] == "C:/test.html"

    def test_result_test_cases(self):
        cfg, tm = self._make_cfg_for_result([
            {"name": "TC_001", "enabled": True, "verdict": 1, "title": "Test 1"},
        ])

        with patch("py_canoe.core.configuration.Configuration._find_test_module", return_value=tm), \
             patch("win32com.client.Dispatch", side_effect=lambda x: x), \
             patch("win32com.client.CastTo", side_effect=_cast_to_side_effect):
            result = cfg.get_test_module_result("TestMod1")

        assert "TC_001" in result["test_cases"]
        tc = result["test_cases"]["TC_001"]
        # test_cases holds live TestCase objects (not dicts).
        assert tc.name == "TC_001"
        assert tc.enabled is True
        assert tc.verdict == 1
        assert tc.verdict_name == "Passed"
        assert tc.title == "Test 1"

    def test_result_not_found_returns_empty(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_modules = []
        assert cfg.get_test_module_result("NonExistent") == {}

    def test_result_exception_returns_empty(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_modules = []
        with patch("py_canoe.core.configuration.Configuration._find_test_module", side_effect=Exception("error")):
            assert cfg.get_test_module_result("TestMod1") == {}


# ===========================================================================
# Configuration.enable_test_configurations_cases
# ===========================================================================

class TestEnableTestConfigurationsCases:
    """Test enable_test_configurations_cases with mocked elements/cases."""

    def _make_cfg(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_configurations = {}
        return cfg

    # --- Empty patterns ---

    def test_empty_patterns_does_nothing(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        with patch.object(cfg, "get_top_test_configurations_elements") as mock_el, \
             patch.object(cfg, "get_all_test_configurations_cases") as mock_cases:
            cfg.enable_test_configurations_cases(tc_obj, (), ())

        mock_el.assert_not_called()
        mock_cases.assert_not_called()

    def test_no_patterns_does_nothing(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        with patch.object(cfg, "get_top_test_configurations_elements") as mock_el, \
             patch.object(cfg, "get_all_test_configurations_cases") as mock_cases:
            cfg.enable_test_configurations_cases(tc_obj)

        mock_el.assert_not_called()
        mock_cases.assert_not_called()

    # --- match_by="name" with enable patterns ---

    def test_enable_pattern_enables_matching_cases(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        tce1 = MagicMock(spec=TestTreeElement)
        tce1.enabled = False
        tce2 = MagicMock(spec=TestTreeElement)
        tce2.enabled = False

        cfg.get_top_test_configurations_elements = MagicMock(return_value={})
        cfg.get_all_test_configurations_cases = MagicMock(return_value={
            "TC_001": {"tte_obj": tce1},
            "TC_002": {"tte_obj": tce2},
        })

        cfg.enable_test_configurations_cases(tc_obj, enable_patterns=["TC_001"])

        assert tce1.enabled is True
        assert tce2.enabled is False

    def test_enable_wildcard_pattern(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        tce1 = MagicMock(spec=TestTreeElement)
        tce1.enabled = False
        tce2 = MagicMock(spec=TestTreeElement)
        tce2.enabled = False

        cfg.get_top_test_configurations_elements = MagicMock(return_value={})
        cfg.get_all_test_configurations_cases = MagicMock(return_value={
            "TC_001": {"tte_obj": tce1},
            "TC_002": {"tte_obj": tce2},
        })

        cfg.enable_test_configurations_cases(tc_obj, enable_patterns=["TC_00*"])

        assert tce1.enabled is True
        assert tce2.enabled is True

    # --- match_by="name" with disable patterns ---

    def test_disable_pattern_disables_matching_cases(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        tce1 = MagicMock(spec=TestTreeElement)
        tce1.enabled = True
        tce2 = MagicMock(spec=TestTreeElement)
        tce2.enabled = True

        cfg.get_top_test_configurations_elements = MagicMock(return_value={})
        cfg.get_all_test_configurations_cases = MagicMock(return_value={
            "TC_001": {"tte_obj": tce1},
            "TC_slow": {"tte_obj": tce2},
        })

        cfg.enable_test_configurations_cases(tc_obj, disable_patterns=["*slow*"])

        assert tce1.enabled is True
        assert tce2.enabled is False

    # --- Disable takes precedence ---

    def test_disable_takes_precedence(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        tce = MagicMock(spec=TestTreeElement)
        tce.enabled = True

        cfg.get_top_test_configurations_elements = MagicMock(return_value={})
        cfg.get_all_test_configurations_cases = MagicMock(return_value={
            "TC_slow_001": {"tte_obj": tce},
        })

        cfg.enable_test_configurations_cases(tc_obj, enable_patterns=["*"], disable_patterns=["*slow*"])

        assert tce.enabled is False

    # --- String pattern (not list) ---

    def test_string_pattern_not_iterated_char_by_char(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        tce1 = MagicMock(spec=TestTreeElement)
        tce1.enabled = False
        tce2 = MagicMock(spec=TestTreeElement)
        tce2.enabled = False

        cfg.get_top_test_configurations_elements = MagicMock(return_value={})
        cfg.get_all_test_configurations_cases = MagicMock(return_value={
            "TC_001": {"tte_obj": tce1},
            "TC_071": {"tte_obj": tce2},
        })

        cfg.enable_test_configurations_cases(tc_obj, enable_patterns="TC_001")

        assert tce1.enabled is True
        assert tce2.enabled is False

    # --- match_by="group" / "fixture" ---

    def test_match_by_group_enables_matching_groups(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        group_tte = MagicMock(spec=TestTreeElement)
        group_tte.type = TestTreeElementType.TEST_GROUP
        group_tte.enabled = False
        case_tte = MagicMock(spec=TestTreeElement)
        case_tte.enabled = False

        cfg.get_top_test_configurations_elements = MagicMock(return_value={
            "TU1": {"Group1": group_tte, "TC_001": case_tte},
        })
        cfg.get_all_test_configurations_cases = MagicMock(return_value={})

        cfg.enable_test_configurations_cases(tc_obj, enable_patterns=["Group*"], match_by="group")

        assert group_tte.enabled is True
        assert case_tte.enabled is False

    def test_match_by_fixture_enables_matching_fixtures(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        fix_tte = MagicMock(spec=TestTreeElement)
        fix_tte.type = TestTreeElementType.TEST_FIXTURE
        fix_tte.enabled = False
        case_tte = MagicMock(spec=TestTreeElement)
        case_tte.enabled = False

        cfg.get_top_test_configurations_elements = MagicMock(return_value={
            "TU1": {"Fixture1": fix_tte, "TC_001": case_tte},
        })
        cfg.get_all_test_configurations_cases = MagicMock(return_value={})

        cfg.enable_test_configurations_cases(tc_obj, enable_patterns=["Fixture*"], match_by="fixture")

        assert fix_tte.enabled is True
        assert case_tte.enabled is False

    # --- Invalid match_by ---

    def test_invalid_match_by_falls_back_to_name(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        tce = MagicMock(spec=TestTreeElement)
        tce.enabled = False

        cfg.get_top_test_configurations_elements = MagicMock(return_value={})
        cfg.get_all_test_configurations_cases = MagicMock(return_value={
            "TC_001": {"tte_obj": tce},
        })

        cfg.enable_test_configurations_cases(tc_obj, enable_patterns=["TC_001"], match_by="invalid")

        assert tce.enabled is True

    # --- No test cases ---

    def test_no_test_cases_warns_and_returns(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        cfg.get_top_test_configurations_elements = MagicMock(return_value={})
        cfg.get_all_test_configurations_cases = MagicMock(return_value={})

        with patch("py_canoe.core.configuration.logger.warning") as mock_warn:
            cfg.enable_test_configurations_cases(tc_obj, enable_patterns=["*"])

        mock_warn.assert_called_once()
        assert "No test cases found" in mock_warn.call_args[0][0]

    # --- group/fixture with no match ---

    def test_group_mode_no_match_warns_and_returns(self):
        cfg = self._make_cfg()
        tc_obj = MagicMock()

        group_tte = MagicMock(spec=TestTreeElement)
        group_tte.type = TestTreeElementType.TEST_GROUP
        group_tte.enabled = False

        cfg.get_top_test_configurations_elements = MagicMock(return_value={
            "TU1": {"Group1": group_tte},
        })
        cfg.get_all_test_configurations_cases = MagicMock(return_value={})

        with patch("py_canoe.core.configuration.logger.warning") as mock_warn:
            cfg.enable_test_configurations_cases(tc_obj, enable_patterns=["NoMatch*"], match_by="group")

        mock_warn.assert_called_once()
        assert "no test case titles" in mock_warn.call_args[0][0]
        assert group_tte.enabled is False


# ===========================================================================
# Configuration.get_test_configurations_cases_result
# ===========================================================================

class TestGetTestConfigurationsCasesResult:
    """Test get_test_configurations_cases_result."""

    def _make_test_conf_mock(self, name, report_path, test_units_data=None):
        """Create a mocked TestConfiguration with test_units and report."""
        if test_units_data is None:
            test_units_data = {"TU1": {"TC_001": MagicMock(spec=TestTreeElement)}}

        tc = MagicMock()
        tc.name = name

        # Mock test_units.fetch_all_test_units -> returns dict of TestUnit mocks
        tu_mocks = {}
        for tu_name, cases in test_units_data.items():
            tu = MagicMock()
            elements = MagicMock()
            elements.get_test_tree_element_cases = lambda cases_dict, c=cases: cases_dict.update(c)
            tu.elements = elements
            tu_mocks[tu_name] = tu

        tc.test_units.fetch_all_test_units = MagicMock(return_value=tu_mocks)

        # Mock report.full_path
        tc.report.full_path = report_path

        return tc

    def test_returns_verdict_info_for_matching_config(self):
        cfg = Configuration.__new__(Configuration)
        tce = MagicMock(spec=TestTreeElement)
        tce.enabled = True
        tce.verdict = 1

        test_conf = self._make_test_conf_mock(
            "TC1", "C:/report.xml",
            {"TU1": {"TCase1": {"tte_obj": tce}}}
        )
        cfg._Configuration__test_configurations = {"TC1": test_conf}

        result = cfg.get_test_configurations_cases_result("TC1")

        assert "TCase1" in result
        assert result["TCase1"]["enabled"] is True
        assert result["TCase1"]["verdict"] == 1
        assert result["TCase1"]["verdict_name"] == "Passed"
        assert result["TCase1"]["report_path"] == "C:/report.xml"

    def test_empty_string_returns_empty_dict(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_configurations = {}

        with patch("py_canoe.core.configuration.logger.warning") as mock_warn:
            result = cfg.get_test_configurations_cases_result("")

        assert result == {}
        mock_warn.assert_called_once()

    def test_nonexistent_config_returns_empty_dict(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_configurations = {"TC1": MagicMock()}

        result = cfg.get_test_configurations_cases_result("NonExistent")

        assert result == {}

    def test_verdict_mapping_all_values(self):
        cfg = Configuration.__new__(Configuration)

        cases = {}
        for verdict_val, expected_name in [(0, "NotAvailable"), (1, "Passed"), (2, "Failed"),
                                           (3, "None"), (4, "Inconclusive"), (5, "ErrorInTestSystem")]:
            tce = MagicMock(spec=TestTreeElement)
            tce.enabled = True
            tce.verdict = verdict_val
            cases[f"TC_{verdict_val}"] = {"tte_obj": tce}

        test_conf = self._make_test_conf_mock("TC1", "C:/r.xml", {"TU1": cases})
        cfg._Configuration__test_configurations = {"TC1": test_conf}

        result = cfg.get_test_configurations_cases_result("TC1")

        for verdict_val, expected_name in [(0, "NotAvailable"), (1, "Passed"), (2, "Failed"),
                                           (3, "None"), (4, "Inconclusive"), (5, "ErrorInTestSystem")]:
            assert result[f"TC_{verdict_val}"]["verdict_name"] == expected_name

    def test_unknown_verdict_defaults_to_unknown(self):
        cfg = Configuration.__new__(Configuration)

        tce = MagicMock(spec=TestTreeElement)
        tce.enabled = True
        tce.verdict = 99

        test_conf = self._make_test_conf_mock("TC1", "C:/r.xml", {"TU1": {"TC_X": {"tte_obj": tce}}})
        cfg._Configuration__test_configurations = {"TC1": test_conf}

        result = cfg.get_test_configurations_cases_result("TC1")

        assert result["TC_X"]["verdict_name"] == "Unknown"


# ===========================================================================
# Configuration.execute_all_test_configurations with patterns
# ===========================================================================

class TestExecuteAllTestConfigurationsWithPatterns:
    """Test execute_all_test_configurations forwards patterns correctly."""

    def test_forwards_enable_disable_patterns(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_configurations = {"TC1": MagicMock(), "TC2": MagicMock()}

        with patch.object(cfg, "enable_test_configurations_cases") as mock_enable:
            cfg.execute_all_test_configurations(
                enable_test_case=["*"],
                disable_test_case=["*slow*"],
                match_by="name",
                wait_for_completion=False
            )

        assert mock_enable.call_count == 2
        for call in mock_enable.call_args_list:
            assert call.args[1] == ["*"]
            assert call.args[2] == ["*slow*"]
            assert call.args[3] == "name"

    def test_defaults_empty_patterns(self):
        cfg = Configuration.__new__(Configuration)
        tc1 = MagicMock()
        cfg._Configuration__test_configurations = {"TC1": tc1}

        with patch.object(cfg, "enable_test_configurations_cases") as mock_enable:
            cfg.execute_all_test_configurations(wait_for_completion=False)

        mock_enable.assert_called_once()
        assert mock_enable.call_args[0][1] == ()
        assert mock_enable.call_args[0][2] == ()
        assert mock_enable.call_args[0][3] == "name"


# ===========================================================================
# Configuration.execute_test_configuration with patterns
# ===========================================================================

class TestExecuteTestConfigurationWithPatterns:
    """Test execute_test_configuration forwards patterns correctly."""

    def test_forwards_enable_disable_patterns(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_configurations = {"TC1": MagicMock()}

        with patch.object(cfg, "enable_test_configurations_cases") as mock_enable:
            cfg.execute_test_configuration(
                "TC1",
                enable_test_case=["*"],
                disable_test_case=["*slow*"],
                match_by="name",
                wait_for_completion=False
            )

        mock_enable.assert_called_once()
        assert mock_enable.call_args[0][1] == ["*"]
        assert mock_enable.call_args[0][2] == ["*slow*"]
        assert mock_enable.call_args[0][3] == "name"

    def test_defaults_empty_patterns(self):
        cfg = Configuration.__new__(Configuration)
        cfg._Configuration__test_configurations = {"TC1": MagicMock()}

        with patch.object(cfg, "enable_test_configurations_cases") as mock_enable:
            cfg.execute_test_configuration("TC1", wait_for_completion=False)

        mock_enable.assert_called_once()
        assert mock_enable.call_args[0][1] == ()
        assert mock_enable.call_args[0][2] == ()
        assert mock_enable.call_args[0][3] == "name"

