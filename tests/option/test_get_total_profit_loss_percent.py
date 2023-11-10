
def test_get_total_profit_loss_percent_raises_exception_if_not_traded():
    test_option = get_test_call_option()

    with pytest.raises(Exception, match="No trade has been opened."):
        test_option.get_total_profit_loss_percent()

@pytest.mark.parametrize("test_option, qty, price, expected_value", [
    (get_test_call_option(), 10, 1.8, 0.2),
    (get_test_call_option(), -10, 1.8, -0.2),
    (get_test_put_option(), 10, 1.8, 0.2),
    (get_test_put_option(), -10, 1.8, -0.2),
])
def test_get_total_profit_loss_percent_returns_unrealized_when_no_contracts_are_closed(
        test_option, qty, price, expected_value):
    test_option = get_test_call_option()
    test_option.open_trade(qty)

    quote_date, spot_price, bid, ask, _ = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)

    actual_value = test_option.get_total_profit_loss_percent()
    assert actual_value == expected_value

@pytest.mark.parametrize("test_option, qty, price, expected_value", [
    (get_test_call_option(), 10, 1.8, 0.2),
    (get_test_call_option(), -10, 1.8, -0.2),
    (get_test_put_option(), 10, 1.8,  0.2),
    (get_test_put_option(), -10, 1.8, -0.2),
])
def test_get_total_profit_loss_percent_returns_closed_pnl_when_all_contracts_are_closed(test_option, qty, price,
                                                                                        expected_value):
    test_option.open_trade(qty)
    quote_date, spot_price, bid, ask, _ = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(qty)

    assert test_option.get_total_profit_loss_percent() == expected_value

@pytest.mark.parametrize("test_option, qty, close_qty_1, close_qty_2, price1, price2, price3, expected_value", [
    (get_test_call_option(), 10, 4, 2, 1.8, 2.2, 0.10, -0.2),
    (get_test_call_option(), -10, -4, -2,  1.8, 2.2, 0.10, 0.2),
    (get_test_call_option(), 10, 4, 2, 3.0, 4.5, 6, 2.0),
    (get_test_call_option(), -10, -4, -2, 3.0, 4.5, 6, -2.0),
])
def test_get_total_profit_loss_percent_returns_unrealized_and_closed_pnl_when_multiple_close_trades(test_option, qty,
                                                                                                    close_qty_1,
                                                                                                    close_qty_2,
                                                                                                    price1, price2,
                                                                                                    price3,
                                                                                                    expected_value):
    test_option.open_trade(qty)
    quote_date, spot_price, bid, ask, _ = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price1)
    it1 = test_option.close_trade(close_qty_1)
    quote_date, spot_price, bid, ask, _ = get_test_call_option_update_values_2()
    test_option.update(quote_date, spot_price, bid, ask, price2)
    it2 = test_option.close_trade(close_qty_2)  # 1050
    quote_date, spot_price, bid, ask, _ = get_test_call_option_update_values_2()
    test_option.update(quote_date, spot_price, bid, ask, price3)  # 2600

    actual_value = test_option.get_total_profit_loss_percent()
    assert actual_value == expected_value