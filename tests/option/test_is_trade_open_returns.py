"""
This module contains tests for the is_trade_open method of the Option class.
"""


def test_is_trade_open_returns_false_if_no_trade_was_opened(call_option):
    """
    Test if the is_trade_open method returns False when no trade was opened.
    """
    test_option = call_option
    expected_result = False
    assert test_option.is_trade_open() == expected_result


def test_is_trade_open_returns_true_if_trade_was_opened(call_option):
    """
    Test if the is_trade_open method returns True when a trade was opened.
    """
    test_option = call_option
    test_option.open_trade(10)
    expected_result = True

    assert test_option.is_trade_open() == expected_result


def test_is_trade_open_returns_true_if_trade_was_opened_and_partially_closed(
    call_option,
):
    """
    Test if the is_trade_open method returns True when a trade was opened and partially closed.
    """
    test_option = call_option
    test_option.open_trade(10)
    test_option.close_trade(5)
    expected_result = True

    assert test_option.is_trade_open() == expected_result


def test_is_trade_open_returns_false_if_trade_was_opened_and_then_closed(call_option):
    """
    Test if the is_trade_open method returns False when a trade was opened and then fully closed.
    """
    test_option = call_option
    test_option.open_trade(10)
    test_option.close_trade(10)
    expected_result = False

    assert test_option.is_trade_open() == expected_result
