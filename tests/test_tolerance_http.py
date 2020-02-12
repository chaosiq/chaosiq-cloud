from chaoscloud.tolerances.http import status_must_be, status_in_range, \
    response_time_under, response_time_above


def test_status_must_be_ok():
    assert status_must_be(200, 200) is True


def test_status_must_be_ko():
    assert status_must_be(400, 200) is False


def test_status_in_range_ok():
    assert status_in_range(200, 100, 300) is True


def test_status_in_range_ok_with_default_upper():
    assert status_in_range(200, 100) is True


def test_status_in_range_ko():
    assert status_in_range(200, 400, 500) is False


def test_response_time_above_ok():
    assert response_time_above(1890.8, 1000) is True


def test_response_time_above_ko():
    assert response_time_above(890.8, 1500.0) is False


def test_response_time_under_ok():
    assert response_time_under(690.8, 1000) is True


def test_response_time_under_ko():
    assert response_time_under(890.8, 500.0) is False
