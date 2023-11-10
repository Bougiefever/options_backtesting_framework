import pytest

from options_framework_archive.option_types import OptionPositionType
import options_framework_archive.option as option
from options_test_helper import *








def test_trade_close_records_returns_all_close_trades():
    test_option = get_test_call_option()
    test_option.open_trade(10)
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)

    test_option.close_trade(quantity=3)

    records = test_option.trade_close_records
    assert len(records) == 1

    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_2()
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(quantity=6)

    records = test_option.trade_close_records
    assert len(records) == 2


def test_total_fees_returns_all_fees_incurred():
    # standard fee is 0.50 per contract
    _id, strike, spot_price, bid, ask, price = (1, 100, 90, 1.0, 2.0, 1.5)
    test_option = Option(_id, ticker, strike, test_expiration, OptionType.CALL,
                         quote_date=test_quote_date, spot_price=spot_price, bid=bid,
                         ask=ask, price=price, fee=standard_fee) # add fee when creating option object

    test_option.open_trade(10)

    assert test_option.total_fees == 5.0

    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(quantity=2)

    assert test_option.total_fees == 6.0

    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(quantity=3)

    assert test_option.total_fees == 7.5











def test_put_option_get_close_price_is_zero_when_option_expires_otm():
    test_option = get_test_put_option()
    test_option.open_trade(1)
    _, spot_price, bid, ask, price = get_test_put_option_update_values_3()
    test_option.update(at_expiration_quote_date, spot_price, bid, ask, price)

    assert test_option.otm()
    assert test_option.option_quote.price != 0.0
    assert test_option.get_closing_price() == 0.0


def test_otm_and_itm_equal_none_when_option_does_not_have_quote_data():
    test_option = Option(1, ticker, 100, test_expiration, OptionType.CALL)

    assert test_option.itm() is None
    assert test_option.otm() is None





def test_get_open_profit_loss_percent_raises_exception_if_trade_was_not_opened():
    test_option = get_test_call_option()

    with pytest.raises(Exception, match="No trade has been opened."):
        test_option.get_open_profit_loss_percent()


@pytest.mark.parametrize("quote_date, expected_days_in_trade", [
    (datetime.datetime.strptime("2021-07-01 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 0),
    (datetime.datetime.strptime("2021-07-01 16:15:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 0),
    (datetime.datetime.strptime("2021-07-07 11:14:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 6),
    (datetime.datetime.strptime("2021-07-13 10:53:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 12),
    (datetime.datetime.strptime("2021-07-15 10:05:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 14),
    (datetime.datetime.strptime("2021-07-16 16:15:00.000000", "%Y-%m-%d %H:%M:%S.%f"), 15)
])
def test_get_days_in_trade(quote_date, expected_days_in_trade):
    test_option = get_test_call_option()
    test_option.open_trade(1)

    _, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)

    assert test_option.get_days_in_trade() == expected_days_in_trade




def test_single_option_properties_return_none_when_property_group_is_none():
    test_option = test_option = Option(id, ticker, 100.0, test_expiration, OptionType.CALL)

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


