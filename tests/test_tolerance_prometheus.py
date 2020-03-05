from chaoscloud.tolerances.prometheus import result_value_above, \
    result_value_under, result_value_between


def test_result_value_above_ok():
    assert result_value_above(1.78, 1) is True


def test_result_value_above_ko():
    assert result_value_above(0.78, 1.0) is False


def test_result_value_under_ok():
    assert result_value_under(0.12, 0.6) is True


def test_result_value_under_ko():
    assert result_value_under(0.89, 0.6) is False


def test_result_value_between_ok():
    assert result_value_between(0.12, 0.1, 0.6) is True


def test_result_value_between_ko():
    assert result_value_between(0.89, 0.3, 0.6) is False
