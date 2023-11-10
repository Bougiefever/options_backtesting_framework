def test_close_trade_closes_entire_position_with_default_values():
    test_option = get_test_call_option()
    quantity = 10
    test_option.open_trade(quantity)
    assert test_option.quantity == quantity

    test_option.close_trade()  # Missing quantity closes entire position

    assert test_option.quantity == 0


@pytest.mark.parametrize(
    "quantity, close_quantity, remaining_quantity",
    [(10, 8, 2), (-10, -8, -2), (10, None, 0), (-10, None, 0)],
)
def test_close_partial_trade(quantity, close_quantity, remaining_quantity):
    test_option = get_test_call_option()
    test_option.open_trade(quantity)
    test_option.close_trade(quantity=close_quantity)

    assert test_option.quantity == remaining_quantity


@pytest.mark.parametrize(
    "open_qty, close1_qty, close2_qty, expected_qty",
    [(10, 2, 8, 0), (10, 2, 3, 5), (-10, -2, -8, 0), (-10, -2, -3, -5)],
)
def test_close_trade_with_multiple_partial_close(
    open_qty, close1_qty, close2_qty, expected_qty
):
    test_option = get_test_call_option()
    test_option.open_trade(open_qty)

    test_option.close_trade(quantity=close1_qty)
    test_option.close_trade(quantity=close2_qty)

    assert test_option.quantity == expected_qty


@pytest.mark.parametrize("open_quantity, close_quantity", [(10, 12), (-10, -12)])
def test_close_trade_with_greater_than_quantity_open_raises_exception(
    open_quantity, close_quantity
):
    test_option = get_test_call_option()
    test_option.open_trade(open_quantity)

    with pytest.raises(
        ValueError, match="Quantity to close is greater than the current open quantity."
    ):
        test_option.close_trade(close_quantity)


@pytest.mark.parametrize(
    "open_qty, close1_qty, close2_qty",
    [(10, 6, 6), (10, 10, 1), (-10, -7, -4), (-10, -10, -1)],
)
def test_close_partial_trade_with_greater_than_remaining_quantity_raises_exception(
    open_qty, close1_qty, close2_qty
):
    test_option = get_test_call_option()
    test_option.open_trade(open_qty)
    test_option.close_trade(quantity=close1_qty)  # close partial trade

    with pytest.raises(
        ValueError, match="Quantity to close is greater than the current open quantity."
    ):
        test_option.close_trade(close2_qty)


@pytest.mark.parametrize(
    "incur_fees_flag, open_quantity, close_quantity, fee_amount",
    [
        (True, 10, 10, 5.0),
        (True, -10, -10, 5.0),
        (True, 10, 2, 1.0),
        (False, 10, 10, 0.0),
        (False, -10, -10, 0.0),
        (False, -10, -2, 0.0),
    ],
)
def test_close_trade_updates_total_fees_incur_fees_flag(
    incur_fees_flag, open_quantity, close_quantity, fee_amount
):
    test_option = get_test_call_option()
    test_option.fee_per_contract = standard_fee
    test_option.open_trade(open_quantity, incur_fees=False)  # do not incur fees on open
    assert test_option.total_fees == 0.0

    test_option.close_trade(quantity=close_quantity, incur_fees=incur_fees_flag)

    assert test_option.total_fees == fee_amount


# "open_qty, close_qty, expected_qty, close_dt, close_price, close_pnl, close_pnl_pct, close_fees", [
#         (10, 10, -10, test_update_quote_date, 10.0, 0.0, 0.0, 5.0),
#         (-10, -10, 10, test_update_quote_date, 10.0, 0.0, 0.0, 5.0),
#         (10, 1, test_update_quote_date, 10.0, 0.0, 0.0, 0.5),
#         (-10, 5, test_update_quote_date, 10.0, 0.0, 0.0, 2.5)
@pytest.mark.parametrize(
    "open_qty, close_qty, expected_qty, close_dt, close_pnl, close_pnl_pct, close_fees",
    [
        (10, 10, -10, test_update_quote_date, 8_500.0, 5.6667, 5.0),
        (-10, -10, 10, test_update_quote_date, -8_500.0, -5.6667, 5.0),
        (10, 1, -1, test_update_quote_date, 850.0, 5.6667, 0.5),
        (-10, -5, 5, test_update_quote_date, -4_250.0, -5.6667, 2.5),
    ],
)
def test_close_trade_values_with_one_close_trade(
    open_qty, close_qty, expected_qty, close_dt, close_pnl, close_pnl_pct, close_fees
):
    test_option = get_test_call_option()
    test_option.fee_per_contract = standard_fee
    test_option.open_trade(open_qty)
    quote_date, spot_price, bid, ask, price = get_test_call_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)
    trade_close_info = test_option.close_trade(close_qty)

    assert trade_close_info.date == quote_date
    assert trade_close_info.quantity == close_qty * -1
    assert trade_close_info.price == price
    assert trade_close_info.profit_loss == close_pnl
    assert trade_close_info.profit_loss_percent == close_pnl_pct
    assert trade_close_info.fees == close_fees
