"""
This module contains tests for the trade_close_records property of the Option class.
"""


def test_trade_close_records_returns_all_close_trades(
    call_option, call_option_update_values_1, call_option_update_values_2
):
    """
    Test that the trade_close_records property returns all close trades.

    Parameters:
    call_option (Option): An instance of the Option class.
    option_update_values_1 (tuple): A tuple containing quote_date, spot_price, bid, ask, price values for the first update.
    option_update_values_2 (tuple): A tuple containing quote_date, spot_price, bid, ask, price values for the second update.
    """
    test_option = call_option
    test_option.open_trade(10)
    quote_date, spot_price, bid, ask, price = call_option_update_values_1
    test_option.update(quote_date, spot_price, bid, ask, price)

    test_option.close_trade(quantity=3)

    records = test_option.trade_close_records
    assert len(records) == 1

    quote_date, spot_price, bid, ask, price = call_option_update_values_2
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(quantity=6)

    records = test_option.trade_close_records
    assert len(records) == 2
