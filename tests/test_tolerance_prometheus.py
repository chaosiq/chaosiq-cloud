from chaoscloud.tolerances.prometheus import result_value_above, \
    result_value_under, result_value_between


def test_result_value_above_ok():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1583406074.984, 1.78]}]
        }
    }
    assert result_value_above(value, 1) is True


def test_result_value_above_ko():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1583406074.984, 0.78]}]
        }
    }
    assert result_value_above(value, 1.0) is False


def test_result_range_vector_ok():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "values": [
                [1583406074.984, 0.78], [1583406074.984, 0.64]]}]
        }
    }
    assert result_value_above(value, 0.5) is True


def test_result_range_vector_ko():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "values": [
                [1583406074.984, 0.78], [1583406074.984, 2.38]]}]
        }
    }
    assert result_value_above(value, 1.5) is False


def test_result_scalar_ok():
    value = {
        "status": "success", "data": {
            "resultType": "scalar",
            "result": [1583406074.984, 0.78]
        }
    }
    assert result_value_above(value, 0.5) is True


def test_result_value_above_with_nan_ko():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1583406074.984, "NaN"]}]
        }
    }
    assert result_value_above(value, 1) is False


def test_result_value_under_ok():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1583406074.984, 0.12]}]
        }
    }
    assert result_value_under(value, 0.6) is True


def test_result_value_under_ko():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1583406074.984, 0.89]}]
        }
    }
    assert result_value_under(value, 0.6) is False


def test_result_value_with_nan_ko():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1583406074.984, "NaN"]}]
        }
    }
    assert result_value_under(value, 0.6) is False


def test_result_value_between_ok():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1583406074.984, 0.23]}]
        }
    }
    assert result_value_between(value, 0.1, 0.6) is True


def test_result_value_between_ko():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1583406074.984, 0.89]}]
        }
    }
    assert result_value_between(value, 0.3, 0.6) is False


def test_result_value_between_with_nan_ko():
    value = {
        "status": "success", "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1583406074.984, "NaN"]}]
        }
    }
    assert result_value_between(value, 0.3, 0.6) is False
