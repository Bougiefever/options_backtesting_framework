"""
This module contains tests for the Option class methods.
"""

import pytest
from options_framework.option import Option
from options_framework.config import settings


@pytest.mark.xfail(reason="int object has no attribute `name`")
@pytest.mark.parametrize(
    "option_type, expected_repr",
    [
        (settings.OptionType.CALL, "<CALL XYZ 100.0 2021-07-16>"),
        (settings.OptionType.PUT, "<PUT XYZ 100.0 2021-07-16>"),
    ],
)
def test_call_option_string_representation(
    call_option, put_option, option_type, expected_repr
):
    """
    Test the string representation of the Option class.
    """
    test_option = call_option if option_type == settings.OptionType.CALL else put_option
    assert str(test_option) == expected_repr


def test_call_option_get_close_price_is_zero_when_option_expires_otm(
    put_option, put_option_update_values_3, at_expiration_quote_date
):
    """
    Test that the closing price of an option is zero when it expires out of the money.
    """
    test_option = put_option
    test_option.open_trade(1)
    _, spot_price, bid, ask, price = put_option_update_values_3
    test_option.update(at_expiration_quote_date, spot_price, bid, ask, price)

    assert test_option.otm()
    assert test_option.option_quote.price != 0.0
    assert test_option.get_closing_price() == 0.0


@pytest.mark.parametrize(
    "option_type, spot_price, strike, expected_value",
    [
        (settings.OptionType.CALL, 99.99, 100.0, True),
        (settings.OptionType.CALL, 100.0, 100.0, False),
        (settings.OptionType.CALL, 100.01, 100.0, False),
        (settings.OptionType.PUT, 99.99, 100.0, False),
        (settings.OptionType.PUT, 100.0, 100.0, False),
        (settings.OptionType.PUT, 100.01, 100.0, True),
    ],
)
def test_call_option_otm(
    ticker, expiration, quote_date, option_type, spot_price, strike, expected_value
):
    """
    Test the out of the money method of the Option class.
    """
    bid, ask, price = (9.50, 10.5, 10.00)
    test_option = Option(
        1,
        ticker,
        100,
        expiration,
        option_type,
        quote_date=quote_date,
        spot_price=spot_price,
        bid=bid,
        ask=ask,
        price=price,
    )

    actual_value = test_option.otm()
    assert actual_value == expected_value


@pytest.mark.parametrize(
    "option_type, spot_price, strike, expected_value",
    [
        (settings.OptionType.CALL, 99.99, 100.0, False),
        (settings.OptionType.CALL, 100.0, 100.0, True),
        (settings.OptionType.CALL, 100.01, 100.0, True),
        (settings.OptionType.PUT, 99.99, 100.0, True),
        (settings.OptionType.PUT, 100.0, 100.0, True),
        (settings.OptionType.PUT, 100.01, 100.0, False),
    ],
)
def test_call_option_itm(
    ticker, expiration, quote_date, option_type, spot_price, strike, expected_value
):
    """
    Test the in the money method of the Option class.
    """
    bid, ask, price = (9.50, 10.5, 10.00)
    test_option = Option(
        1,
        ticker,
        100,
        expiration,
        option_type,
        quote_date=quote_date,
        spot_price=spot_price,
        bid=bid,
        ask=ask,
        price=price,
    )

    actual_value = test_option.itm()
    assert actual_value == expected_value


@pytest.mark.parametrize(
    "open_qty, cqty1, cqty2, close_price, close_pnl, pnl_pct, close_fees, closed_qty, remaining_qty",
    [
        (10, 2, 3, 7.0, 2_750.0, 1.8333, 2.5, -5, 5),
        (-10, -3, -5, 6.88, -4_300, -2.8667, 4.0, 8, -2),
        (10, 8, 1, 9.44, 7_150.0, 4.7667, 4.5, -9, 1),
        (-10, -1, -1, 7.5, -1_200.0, -0.8000, 1.0, 2, -8),
    ],
)
def test_call_option_close_trade_values_with_multiple_close_trades(
    call_option,
    call_option_update_values_1,
    call_option_update_values_2,
    standard_fee,
    update_quote_date2,
    open_qty,
    cqty1,
    cqty2,
    close_price,
    close_pnl,
    pnl_pct,
    close_fees,
    closed_qty,
    remaining_qty,
):
    """
    Test the close trade method of the Option class with multiple close trades.
    """
    close_date = update_quote_date2
    test_option = call_option
    test_option.fee_per_contract = standard_fee
    test_option.open_trade(open_qty)
    # first update
    quote_date, spot_price, bid, ask, price = call_option_update_values_1
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(quantity=cqty1)

    # second update
    quote_date, spot_price, bid, ask, price = call_option_update_values_2
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(quantity=cqty2)

    # get close info for closed trades
    trade_close_info = test_option.get_trade_close_info()
    assert trade_close_info.date == close_date
    assert trade_close_info.price == close_price
    assert trade_close_info.profit_loss == close_pnl
    assert trade_close_info.fees == close_fees

    assert trade_close_info.quantity == closed_qty
    assert test_option.quantity == remaining_qty
