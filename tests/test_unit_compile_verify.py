from unittest.mock import MagicMock
from py_canoe.core.configuration import Configuration


def _make_configuration(compile_raises=False):
    cfg = Configuration.__new__(Configuration)
    com = MagicMock()
    if compile_raises:
        com.CompileAndVerify.side_effect = Exception("COM error")
    cfg.com_object = com
    return cfg


class TestCompileAndVerifyInternal:
    def test_returns_success_dict_on_success(self):
        cfg = _make_configuration()
        result = cfg._compile_and_verify_internal()
        assert result == {"success": True, "error": None}

    def test_returns_failure_dict_on_exception(self):
        cfg = _make_configuration(compile_raises=True)
        result = cfg._compile_and_verify_internal()
        assert result["success"] is False
        assert "COM error" in result["error"]

    def test_calls_com_exactly_once(self):
        cfg = _make_configuration()
        cfg._compile_and_verify_internal()
        cfg.com_object.CompileAndVerify.assert_called_once()


class TestGetCompilationResult:
    def test_delegates_to_internal(self):
        cfg = _make_configuration()
        result = cfg.get_compilation_result()
        cfg.com_object.CompileAndVerify.assert_called_once()
        assert result["success"] is True
        assert result["error"] is None

    def test_returns_failure_dict_on_exception(self):
        cfg = _make_configuration(compile_raises=True)
        result = cfg.get_compilation_result()
        assert result["success"] is False
        assert "COM error" in result["error"]

    def test_return_dict_has_correct_keys(self):
        cfg = _make_configuration()
        result = cfg.get_compilation_result()
        assert set(result.keys()) == {"success", "error"}

    def test_return_type_is_dict(self):
        cfg = _make_configuration()
        result = cfg.get_compilation_result()
        assert isinstance(result, dict)


class TestRunCompilation:
    def test_returns_true_on_success(self):
        cfg = _make_configuration()
        result = cfg.run_compilation()
        cfg.com_object.CompileAndVerify.assert_called_once()
        assert result is True

    def test_returns_false_on_exception(self):
        cfg = _make_configuration(compile_raises=True)
        result = cfg.run_compilation()
        assert result is False

    def test_return_type_is_bool(self):
        cfg = _make_configuration()
        result = cfg.run_compilation()
        assert isinstance(result, bool)
