

def test_get_profit_loss_percent_return_zero_when_no_contracts_are_open():
    test_option = get_test_call_option()
    test_option.open_trade(1)
    test_option.close_trade(1)

    assert test_option.get_open_profit_loss_percent() == 0.0


@pytest.mark.parametrize("test_option, quantity, price, expected_profit_loss_pct", [
    (get_test_call_option(), 10, 2.25, 0.5),
    (get_test_call_option(), 10, 1.17, -0.22),
    (get_test_call_option(), 10, 1.5, 0.0),
    (get_test_call_option(), -10, 2.25, -0.50),
    (get_test_call_option(), -10, 1.17, 0.22),
    (get_test_call_option(), -10, 1.5, 0.0),
    (get_test_put_option(), 10, 2.25, 0.5),
    (get_test_put_option(), 10, 1.17, -0.22),
    (get_test_put_option(), 10, 1.5, 0.0),
    (get_test_put_option(), -10, 2.25, -0.50),
    (get_test_put_option(), -10, 1.17, 0.22),
    (get_test_put_option(), -10, 1.5, 0.0)
])
def test_get_profit_loss_percent_value(test_option, quantity, price, expected_profit_loss_pct):
    test_option.open_trade(quantity)
    quote_date, spot_price, bid, ask, _ = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)

    actual_profit_loss = test_option.get_open_profit_loss_percent()
    assert actual_profit_loss == expected_profit_loss_pct