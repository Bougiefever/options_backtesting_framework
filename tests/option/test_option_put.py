


def test_put_option_get_close_price_is_zero_when_option_expires_otm():
    test_option = get_test_put_option()
    test_option.open_trade(1)
    _, spot_price, bid, ask, price = get_test_put_option_update_values_3()
    test_option.update(at_expiration_quote_date, spot_price, bid, ask, price)

    assert test_option.otm()
    assert test_option.option_quote.price != 0.0
    assert test_option.get_closing_price() == 0.0


@pytest.mark.parametrize(
    "open_qty, cqty1, cqty2, close_date, close_price, close_pnl, pnl_pct, close_fees, closed_qty, remaining_qty",
    [(10, 2, 3, test_update_quote_date2, 7.0, 2_750.0, 1.8333, 2.5, -5, 5),
     (-10, -3, -5, test_update_quote_date2, 6.88, -4_300, -2.8667, 4.0, 8, -2),
     (10, 8, 1, test_update_quote_date2, 9.44, 7_150.0, 4.7667, 4.5, -9, 1),
     (-10, -1, -1, test_update_quote_date2, 7.5, -1_200.0, -0.8000, 1.0, 2, -8)
     ])
def test_put_option_close_trade_values_with_multiple_close_trades(open_qty, cqty1, cqty2, close_date, close_price,
                                                                   close_pnl, pnl_pct, close_fees,
                                                                   closed_qty, remaining_qty):
    test_option = get_test_put_option()
    test_option.fee_per_contract = standard_fee
    test_option.open_trade(open_qty)
    # first update
    quote_date, spot_price, bid, ask, price = get_test_put_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(quantity=cqty1)

    # second update
    quote_date, spot_price, bid, ask, price = get_test_put_option_update_values_2()
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