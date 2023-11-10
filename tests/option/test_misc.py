"""
This module contains tests for the Option class in the options_framework package.
"""

from datetime import datetime
import pytest

from options_framework.config import settings
from options_framework.option import Option


def test_total_fees_returns_all_fees_incurred(
    ticker,
    expiration,
    quote_date,
    standard_fee,
    call_option_update_values_1,
):
    """
    Test that the total_fees method correctly calculates all fees incurred.
    """
    assert isinstance(quote_date, datetime)
    # standard fee is 0.50 per contract
    _id, strike, spot_price, bid, ask, price = (1, 100, 90, 1.0, 2.0, 1.5)
    test_option = Option(
        _id,
        ticker,
        strike,
        expiration,
        settings.OptionType.CALL,
        quote_date=quote_date,
        spot_price=spot_price,
        bid=bid,
        ask=ask,
        price=price,
        fee=standard_fee,
    )  # add fee when creating option object

    test_option.open_trade(10)

    assert test_option.total_fees == 5.0

    _quote_date, spot_price, bid, ask, price = call_option_update_values_1
    test_option.update(_quote_date, spot_price, bid, ask, price)
    test_option.close_trade(quantity=2)

    assert test_option.total_fees == 6.0

    _quote_date, spot_price, bid, ask, price = call_option_update_values_1
    test_option.update(_quote_date, spot_price, bid, ask, price)
    test_option.close_trade(quantity=3)

    assert test_option.total_fees == 7.5


def test_otm_and_itm_equal_none_when_option_does_not_have_quote_data(
    ticker, expiration
):
    """
    Test that the itm and otm methods return None when the option does not have quote data.
    """
    test_option = Option(1, ticker, 100, expiration, settings.OptionType.CALL)

    assert test_option.itm() is None
    assert test_option.otm() is None



def test_get_open_profit_loss_percent_raises_exception_if_trade_was_not_opened(
    call_option,
):
    """
    Test that the get_open_profit_loss_percent method raises an exception if a trade was not opened.
    """
    test_option = call_option

    with pytest.raises(Exception, match="No trade has been opened."):
        test_option.get_open_profit_loss_percent()



@pytest.mark.parametrize(
    "current_quote_date, expected_days_in_trade",
    [
        (datetime.strptime("2021-07-01 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 0),
        (datetime.strptime("2021-07-01 16:15:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 0),
        (datetime.strptime("2021-07-07 11:14:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 6),
        (datetime.strptime("2021-07-13 10:53:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 12),
        (datetime.strptime("2021-07-15 10:05:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 14),
        (datetime.strptime("2021-07-16 16:15:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 15),
    ],
)
def test_get_days_in_trade(
    current_quote_date,
    expected_days_in_trade,
    call_option,
    call_option_update_values_1,
):
    """
    Test that the get_days_in_trade method correctly calculates the number of days in a trade.
    """
    test_option = call_option
    test_option.open_trade(1)

    _, spot_price, bid, ask, price = call_option_update_values_1
    test_option.update(current_quote_date, spot_price, bid, ask, price)

    assert test_option.get_days_in_trade() == expected_days_in_trade


def test_single_option_properties_return_none_when_property_group_is_none(
    expiration, ticker
):
    """
    Test that the properties of a single option return None when the property group is None.
    """
    test_option = test_option = Option(
        id, ticker, 100.0, expiration, settings.OptionType.CALL
    )

    assert test_option.option_quote is None
    assert test_option.quote_date is None
    assert test_option.spot_price is None
    assert test_option.bid is None
    assert test_option.ask is None
    assert test_option.price is None

    assert test_option.greeks is None
    assert test_option.delta is None
    assert test_option.gamma is None
    assert test_option.theta is None
    assert test_option.vega is None
    assert test_option.rho is None

    assert test_option.extended_properties is None
    assert test_option.open_interest is None
    assert test_option.implied_volatility is None
