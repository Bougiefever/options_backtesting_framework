
def test_get_close_price_on_option_that_has_not_been_traded_raises_exception():
    test_option = get_test_call_option()
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)

    with pytest.raises(ValueError,
                       match="Cannot determine closing price on option that does not have an opening trade"):
        test_option.get_closing_price()




@pytest.mark.parametrize("open_qty, expected_closing_price", [
    (1, 0.0), (-1, 0.05)
])
def test_get_closing_price_on_call_option_when_bid_is_zero(open_qty, expected_closing_price):
    test_option = get_test_call_option()
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)

    # open trade
    test_option.open_trade(open_qty)
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_3()
    assert bid == 0.0
    test_option.update(quote_date, spot_price, bid, ask, price)

    assert test_option.get_closing_price() == expected_closing_price

@pytest.mark.parametrize("open_qty, expected_closing_price", [
    (1, 0.0), (-1, 0.05)
])
def test_get_closing_price_on_put_option_when_bid_is_zero(open_qty, expected_closing_price):
    test_option = get_test_put_option()
    quote_date, spot_price, bid, ask, price = get_test_put_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)

    # open trade
    test_option.open_trade(open_qty)
    quote_date, spot_price, bid, ask, price = get_test_put_option_update_values_3()
    assert bid == 0.0
    test_option.update(quote_date, spot_price, bid, ask, price)

    assert test_option.get_closing_price() == expected_closing_price

def test_get_closing_price():
    test_option = get_test_call_option()
    test_option.open_trade(1)
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)
    expected_close_price = 10.0

    close_price = test_option.get_closing_price()

    assert close_price == expected_close_price