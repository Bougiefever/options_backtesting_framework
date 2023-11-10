
def test_get_total_profit_loss_raises_exception_if_not_traded():
    test_option = get_test_call_option()

    with pytest.raises(Exception, match="No trade has been opened."):
        test_option.get_total_profit_loss()

@pytest.mark.parametrize("test_option, qty, price, expected_value", [
    (get_test_call_option(), 10, 2.0, 500.0),
    (get_test_call_option(), -10, 2.0, -500.0),
    (get_test_put_option(), 10, 2.0, 500.0),
    (get_test_put_option(), -10, 2.0, -500.0),
])
def test_get_total_profit_loss_returns_unrealized_when_no_contracts_are_closed(test_option, qty, price, expected_value):
    test_option = get_test_call_option()
    test_option.open_trade(qty)

    quote_date, spot_price, bid, ask, _ = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)

    assert test_option.get_total_profit_loss() == expected_value


def test_get_total_profit_loss_returns_closed_pnl_when_all_contracts_are_closed():
    test_option = get_test_call_option()
    test_option.open_trade(10)
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(10)

    assert test_option.get_total_profit_loss() == 8_500.0

def test_get_total_profit_loss_returns_unrealized_and_closed_pnl_when_partially_closed():
    test_option = get_test_call_option()
    test_option.open_trade(10)
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(5)  # 4250
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_2()
    test_option.update(quote_date, spot_price, bid, ask, price)  # 1750

    assert test_option.get_total_profit_loss() == 6_000.0

def test_get_total_profit_loss_returns_unrealized_and_closed_pnl_when_multiple_close_trades():
    test_option = get_test_call_option()
    test_option.open_trade(10)
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(3)  # 2550
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_2()
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(3)  # 1050
    quote_date, spot_price, bid, ask, _ = get_test_call_option_update_values_2()
    test_option.update(quote_date, spot_price, bid, ask, 8.0)  # 2600

    actual_value = test_option.get_total_profit_loss()
    assert actual_value == 6_200.0