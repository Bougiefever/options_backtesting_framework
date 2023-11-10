"""
This module contains tests for the open_trade method of the Option class.
"""

import pytest
from options_framework.config import settings
from options_framework.option import Option


# open trade
def test_open_trade_sets_correct_trade_open_info_values(call_option, quote_date):
    """
    Test that the open_trade method sets the correct trade open info values.
    """
    test_option = call_option
    quantity = 10

    trade_open_info = test_option.open_trade(
        quantity, comment="my super insightful comment"
    )
    assert trade_open_info.date == quote_date
    assert trade_open_info.quantity == 10
    assert trade_open_info.price == 1.5
    assert trade_open_info.premium == 1_500.0
    assert test_option.quantity == 10

    # kwargs were set as attributes
    assert test_option.comment == "my super insightful comment"


def test_option_that_is_not_open_has_none_position_type(call_option):
    """
    Test that an option that is not open has none position type.
    """
    test_option = call_option
    assert test_option.position_type is None


@pytest.mark.parametrize(
    "quantity, position_type",
    [(10, settings.OptionPositionType.LONG), (-10, settings.OptionPositionType.SHORT)],
)
def test_open_trade_has_correct_position_type(quantity, position_type, call_option):
    """
    Test that open_trade has the correct position type.
    """
    test_option = call_option
    test_option.open_trade(quantity)

    assert test_option.position_type == position_type


@pytest.mark.parametrize(
    "option_type, quantity, expected_premium",
    [
        ("call", 10, 1_500.0),
        ("call", 5, 750.0),
        ("call", -10, -1_500.0),
        ("put", 10, 1_500.0),
        ("put", -10, -1_500.0),
        ("put", 5, 750.0),
    ],
)
def test_open_trade_returns_correct_premium_value(
    option_type, quantity, expected_premium, call_option, put_option
):
    """
    Test that open_trade returns the correct premium value.
    """
    option = call_option if option_type == "call" else put_option
    trade_open_info = option.open_trade(quantity)
    assert trade_open_info.premium == expected_premium


@pytest.mark.parametrize(
    "quantity, incur_fees_flag, expected_fees",
    [
        (10, True, 5.0),
        (2, True, 1.0),
        (-3, True, 1.5),
        (10, False, 0.0),
        (2, False, 0.0),
        (-3, False, 0.0),
    ],
)
def test_open_trade_sets_total_fees_when_incur_fees_flag_is_true(
    quantity, incur_fees_flag, expected_fees, call_option, standard_fee
):
    """
    Test that open_trade sets total fees when incur_fees_flag is true.
    """
    test_option = call_option
    test_option.fee_per_contract = standard_fee
    test_option.open_trade(quantity=quantity, incur_fees=incur_fees_flag)

    assert test_option.total_fees == expected_fees


def test_open_trade_when_there_is_no_quote_data_raises_exception(ticker, expiration):
    """
    Test that open_trade raises an exception when there is no quote data.
    """
    test_option = Option(1, ticker, 100, expiration, settings.OptionType.CALL)
    with pytest.raises(
        ValueError, match="Cannot open a position that does not have price data"
    ):
        test_option.open_trade(1)


@pytest.mark.parametrize("quantity", [None, 1.5, 0, -1.5, "abc"])
def test_open_trade_with_invalid_quantity_raises_exception(quantity, call_option):
    """
    Test that open_trade raises an exception with invalid quantity.
    """
    test_option = call_option

    with pytest.raises(ValueError, match="Quantity must be a non-zero integer."):
        test_option.open_trade(quantity)


def test_open_trade_when_trade_is_already_open_raises_exception(call_option):
    """
    Test that open_trade raises an exception when trade is already open.
    """
    test_option = call_option
    quantity = 10
    test_option.open_trade(quantity)

    with pytest.raises(
        ValueError, match="Cannot open position. A position is already open."
    ):
        test_option.open_trade(quantity)
