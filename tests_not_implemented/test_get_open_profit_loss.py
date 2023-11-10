def test_get_open_profit_loss_raises_exception_if_trade_was_not_opened():
    test_option = get_test_call_option()

    with pytest.raises(Exception, match="No trade has been opened."):
        test_option.get_open_profit_loss()


def test_get_open_profit_loss_is_zero_if_quote_data_is_not_updated():
    test_option = get_test_call_option()
    test_option.open_trade(10)

    assert test_option.get_open_profit_loss() == 0.0


def test_get_open_profit_loss_is_zero_when_no_contracts_are_open():
    test_option = get_test_call_option()
    test_option.open_trade(10)
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(10)

    assert test_option.get_open_profit_loss() == 0.0


@pytest.mark.parametrize(
    "test_option, quantity, price, expected_profit_loss",
    [
        (get_test_call_option(), 10, 1.6, 100.0),
        (get_test_call_option(), 10, 1.4, -100.0),
        (get_test_call_option(), 10, 1.5, 0.0),
        (get_test_call_option(), -10, 1.6, -100.0),
        (get_test_call_option(), -10, 1.4, 100.0),
        (get_test_call_option(), -10, 1.5, 0.0),
        (get_test_put_option(), 10, 1.6, 100.0),
        (get_test_put_option(), 10, 1.4, -100.0),
        (get_test_put_option(), 10, 1.5, 0.0),
        (get_test_put_option(), -10, 1.6, -100.0),
        (get_test_put_option(), -10, 1.4, 100.0),
        (get_test_put_option(), -10, 1.5, 0.0),
    ],
)
def test_get_open_profit_loss_value(test_option, quantity, price, expected_profit_loss):
    test_option.open_trade(quantity)
    quote_date, spot_price, bid, ask, _ = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)

    actual_profit_loss = test_option.get_open_profit_loss()
    assert actual_profit_loss == expected_profit_loss
