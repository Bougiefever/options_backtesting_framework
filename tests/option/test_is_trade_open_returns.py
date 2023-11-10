

def test_is_trade_open_returns_false_if_no_trade_was_opened():
    test_option = get_test_call_option()
    expected_result = False
    assert test_option.is_trade_open() == expected_result


def test_is_trade_open_returns_true_if_trade_was_opened():
    test_option = get_test_call_option()
    test_option.open_trade(10)
    expected_result = True

    assert test_option.is_trade_open() == expected_result


def test_is_trade_open_returns_true_if_trade_was_opened_and_partially_closed():
    test_option = get_test_call_option()
    test_option.open_trade(10)
    test_option.close_trade(5)
    expected_result = True

    assert test_option.is_trade_open() == expected_result


def test_is_trade_open_returns_false_if_trade_was_opened_and_then_closed():
    test_option = get_test_call_option()
    test_option.open_trade(10)
    test_option.close_trade(10)
    expected_result = False

    assert test_option.is_trade_open() == expected_result

