"""
This module contains tests for the update method of the Option class.
"""

from datetime import datetime
import pytest


def test_update_sets_correct_values(call_option_extended_properties, update_quote_date):
    """
    Test that the update method correctly sets the values of an option.
    """
    call = call_option_extended_properties

    spot_price, bid, ask, price, delta, gamma, theta, vega, open_interest, rho, iv = (
        95,
        3.4,
        3.50,
        3.45,
        0.4714,
        0.1239,
        -0.0401,
        0.1149,
        1000,
        0.279,
        0.3453,
    )
    test_value = "test value"
    call.update(
        update_quote_date,
        spot_price,
        bid,
        ask,
        price,
        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
        rho=rho,
        implied_volatility=iv,
        open_interest=open_interest,
        user_defined=test_value,
    )

    assert call.option_quote.spot_price == spot_price
    assert call.option_quote.quote_date == update_quote_date
    assert call.option_quote.bid == bid
    assert call.option_quote.ask == ask
    assert call.greeks.delta == delta
    assert call.greeks.gamma == gamma
    assert call.greeks.theta == theta
    assert call.greeks.vega == vega
    assert call.greeks.rho == rho
    assert call.extended_properties.open_interest == open_interest
    assert call.extended_properties.implied_volatility == iv
    assert call.user_defined == test_value


def test_update_raises_exception_if_missing_required_fields(
    call_option, update_quote_date
):
    """
    Test that the update method raises an exception if any required fields are missing.
    """
    test_option = call_option

    # quote_date
    none_quote_date = None
    with pytest.raises(ValueError, match="quote_date is required"):
        test_option.update(
            quote_date=none_quote_date,
            spot_price=90.0,
            bid=1.0,
            ask=2.0,
            price=1.5,
        )

    # spot price
    none_spot_price = None
    with pytest.raises(ValueError, match="spot_price is required"):
        test_option.update(
            quote_date=update_quote_date,
            spot_price=none_spot_price,
            bid=1.0,
            ask=2.0,
            price=1.5,
        )

    # bid
    none_bid = None
    with pytest.raises(ValueError, match="bid is required"):
        test_option.update(
            quote_date=update_quote_date,
            spot_price=90.0,
            bid=none_bid,
            ask=2.0,
            price=1.5,
        )

    # ask
    none_ask = None
    with pytest.raises(ValueError, match="ask is required"):
        test_option.update(
            quote_date=update_quote_date,
            spot_price=90.0,
            bid=1.0,
            ask=none_ask,
            price=1.5,
        )

    # price
    none_price = None
    with pytest.raises(ValueError, match="price is required"):
        test_option.update(
            quote_date=update_quote_date,
            spot_price=90.0,
            bid=1.0,
            ask=2.0,
            price=none_price,
        )


def test_update_raises_exception_if_quote_date_is_greater_than_expiration(put_option):
    """
    Test that the update method raises an exception if the quote date is greater than the expiration date.
    """
    bad_quote_date = datetime.strptime(
        "2021-07-17 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f"
    )
    put = put_option
    spot_price, bid, ask, price = (105, 1.0, 2.0, 1.5)
    with pytest.raises(
        Exception, match="Cannot update to a date past the option expiration"
    ):
        put.update(bad_quote_date, spot_price, bid, ask, price)
